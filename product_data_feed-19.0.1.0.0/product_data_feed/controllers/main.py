# Copyright © 2020 Garazd Creation (https://garazd.biz)
# @author: Yurii Razumovskyi (support@garazd.biz)
# @author: Iryna Razumovska (support@garazd.biz)
# License OPL-1 (https://www.odoo.com/documentation/15.0/legal/licenses.html).

import bz2
import logging
import threading
from gzip import GzipFile
from zipfile import ZipFile

from io import BytesIO
from werkzeug.exceptions import Forbidden, NotFound

from markupsafe import Markup
from odoo import _, http, models
from odoo.http import request, content_disposition, Response

_logger = logging.getLogger(__name__)


class ProductFeed(http.Controller):

    def _validate_feed_request(self, feed_id, feed_name, **kwargs):
        """Check a feed request.

        :param string feed_id: a feed id
        :return: http response or True if everything is ok
        """
        if not (feed_id or feed_name):
            raise NotFound()
        try:
            if feed_id:
                domain = [('id', '=', int(feed_id))]
            else:
                domain = [('filename', '=', str(feed_name))]
            feed = request.env['product.data.feed'].search(domain, limit=1)
        except ValueError:
            raise NotFound()
        if not feed:
            raise NotFound()

        # Check website
        if feed.website_ids and request.website not in feed.website_ids:
            raise NotFound()

        # Check token
        if feed.use_token:
            access_token = kwargs.get('access_token')
            if not access_token or feed.access_token != access_token:
                raise Forbidden()

        return feed

    def _get_mimetype(self, file_type) -> str or None:
        """Determinate a mimetype for a feed.

        :param string file_type: a feed file_type value
        :return: string or None
        """
        mimetypes = {
            'csv': 'text/csv;charset=utf-8',
            'tsv': 'text/tab-separated-values;charset=utf-8',
            'xml': 'application/xml;charset=utf-8',
            'zip': 'application/zip',
            'gz': 'application/gzip',
            'bz2': 'application/x-bzip2',
        }
        return mimetypes.get(file_type, None)

    @http.route([
        '/product_data/<model("product.data.feed"):feed_id>/feed.csv',
        '/product_data/<string:feed_name>.csv',
        '/product_data/<model("product.data.feed"):feed_id>/feed.xml',
        '/product_data/<string:feed_name>.xml',
    ],
        type='http',
        auth='public',
        website=True,
        multilang=False,
        sitemap=False,
    )
    def product_data_feed(self, feed_id=None, feed_name=None, **kwargs):
        """Controller to return CSV/TSV product data feed."""

        feed = self._validate_feed_request(feed_id, feed_name, **kwargs)
        if not isinstance(feed, models.BaseModel):
            return feed

        preview_mode = kwargs.get('preview_mode') == 'True'
        filetype = feed.compress_type if feed.do_compress and not preview_mode else feed.file_type
        mimetype = self._get_mimetype(filetype)
        if not mimetype:
            raise NotFound()

        if feed.with_traceback:
            file = feed.sudo().generate_data_file()
        else:
            try:
                file = feed.sudo().generate_data_file()
            except Exception as e:
                msg = _("Error: %s", str(e))
                _logger.error(msg)
                test_mode = getattr(threading.current_thread(), 'testing', False) \
                            or request.env.registry.in_test_mode()
                if not test_mode:
                    feed.sudo().message_post(body=Markup("<p class='text-danger'>%s</p>") % msg)
                return Response(response="<b>Feed generation error</b>: %s" % str(e), status=404)

        filename = feed._get_file_name()
        headers = [('Content-Type', mimetype)]

        # Feed content with Compression
        if filetype in ('zip', 'gz', 'bz2') and not preview_mode:
            buffer = BytesIO()

            if filetype == 'zip':
                with ZipFile(file=buffer, mode='w') as zipf:
                    zipf.writestr(filename, file)

            elif filetype == 'gz':
                with GzipFile(filename=filename, fileobj=buffer, mode='wb') as gzipf:
                    if isinstance(file, str):
                        file = file.encode()
                    gzipf.write(file)

            else:
                with bz2.open(buffer, mode='wb') as bz2f:
                    if isinstance(file, str):
                        file = file.encode()
                    bz2f.write(file)

            content = buffer.getvalue()
            headers += [
                ('Content-Length', len(file)),
                ('Content-Disposition', content_disposition(f'{filename}.{filetype}')),
            ]

       # Feed content without Compression
        else:
            content = file
            if feed.content_disposition == 'attachment':
                headers += [
                    ('Content-Length', len(file)),
                    ('Content-Disposition', content_disposition(filename)),
                ]

        if feed.debug_mode:
            feed.sudo().message_post(body=Markup("<p class='text-info'>%s</p>") % _("The feed has been read."))

        return request.make_response(content, headers)

    @http.route(['/product_data/preview_csv/<int:feed_id>'], type='http', auth='user')
    def preview_csv(self, feed_id):
        """Controller to preview CSV feed as HTML table."""
        feed = request.env['product.data.feed'].browse(feed_id)

        if not feed or feed and feed.file_type not in ['csv', 'tsv']:
            raise NotFound()

        try:
            csv_file = feed.generate_data_file()
        except Exception as e:
            msg = _('CSV preview error: %s', e)
            _logger.error(msg)
            return request.make_response('<h4>Error generating CSV preview</h4>', status=500)

        html = '''<html>
                    <head>
                        <title>CSV preview</title>
                        <style>
                            table {
                                border-collapse: collapse;
                                width: 100%;
                                font-size: small;
                            }
                            td {
                                border: 1px solid #ccc;
                                padding: 6px 10px;
                            }
                            th {
                                border: 1px solid #ccc;
                                padding: 6px;
                                font-weight: 600;
                            }
                            tr:nth-child(even) {
                                background-color: #f9f9f9;
                            }
                        </style>
                    </head>
                    <body>
                        <table>
                            {inner_content}
                        </table>
                    </body>
                </html>'''

        inner_content = '\n'
        for index, row in enumerate(csv_file.split('\n')):
            inner_content += '<tr>\n'
            tag_name = 'th' if index == 0 else 'td'
            for column in row.split(f'"{feed.text_separator}"'):
                content = column.strip('"')
                inner_content += f'    <{tag_name}>{content}</{tag_name}>\n'
            inner_content += '</tr>\n'

        return request.make_response(
            html.replace('{inner_content}', inner_content),
            [('Content-type', 'text/html; charset=utf-8')]
        )
