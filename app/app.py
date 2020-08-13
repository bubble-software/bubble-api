import falcon
import logging
from falcon.http_status import HTTPStatus
from app.util.db_connection import DbConnection
from app.services.add_post_to_category import AddPostService
from app.services.remove_post_from_category import RemovePostService
from app.services.feed import FeedService
from app.services.category import CategoryService


class Service:
	def __init__(self):
		print('Initializing Chart Service...')
		self.dbconnection = DbConnection('db_credentials.yaml')

def start_service():
	service = Service()
	add_post_service = AddPostService(service)
	remove_post_service = RemovePostService(service)
	feed_service = FeedService(service)
	category_service = CategoryService(service)

	app = falcon.API(middleware=[HandleCORS()])
	app.add_route('/add_post_to_category', add_post_service)
	app.add_route('/remove_post_from_category', remove_post_service)
	app.add_route('/feed', feed_service)
	app.add_route('/category', category_service)
	return app

class HandleCORS(object):
	def process_request(self, req, resp):
		resp.set_header('Access-Control-Allow-Origin', '*')
		resp.set_header('Access-Control-Allow-Methods', '*')
		resp.set_header('Access-Control-Allow-Headers', '*')
		resp.set_header('Access-Control-Max-Age', 1728000)  # 20 days
		if req.method == 'OPTIONS':
			raise HTTPStatus(falcon.HTTP_200, body='\n')

if __name__ != '__main__':
	gunicorn_logger = logging.getLogger('gunicorn.error')