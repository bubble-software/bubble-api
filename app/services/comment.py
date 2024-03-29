import falcon
import sys
import psycopg2.extras
from datetime import datetime, timezone
from falcon.http_status import HTTPStatus
from app.queries_new_schema import QUERY_CHECK_CONNECTION, QUERY_INSERT_COMMENT, QUERY_GET_COMMENT, QUERY_INSERT_NOTIFCATIONS_COMMENTS

class CommentService:
	def __init__(self, service):
		print('Initializing Comment Service...')
		self.service = service
	
	def on_get(self, req, resp):
		print('HTTP GET: /comment')
		print(req.params)
		self.service.dbconnection.init_db_connection()
		con = self.service.dbconnection.connection
		cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
		token = req.params['token']
		decode = self.service.jwt.decode_auth_token(token)
		cursor.execute(QUERY_GET_COMMENT, (decode['user_id'], req.params['post_id'], decode['user_id']))
		response = []
		for record in cursor:
			response.append(
				{
					'id': record[0],
					'user_id': record[1],
					'content': record[2],
					'date_created': str(record[3]),
					'username': record[4],
					'votes': record[5],
					'is_voted': record[6],
					'prev_vote': record[7]
					
				}
			)
		cursor.close()
		con.close()
		
		resp.status = falcon.HTTP_200
		resp.media = response
		
	def on_post(self, req, resp):
		self.service.dbconnection.init_db_connection()
		con = self.service.dbconnection.connection
		try:
			print('HTTP POST: /comment')
			cursor = con.cursor()
			print(req.media)
			token = req.headers['AUTHORIZATION']
			decode = self.service.jwt.decode_auth_token(token)
			cursor.execute(QUERY_INSERT_COMMENT, (
					decode['user_id'],
					req.media['content'],
					datetime.now(tz=timezone.utc),
					req.media['post_id'],
				)
			)
			
			if req.media.get('notify') is not None and req.media['notify'] == True:
				cursor.execute(QUERY_INSERT_NOTIFCATIONS_COMMENTS, (
						decode['user_id'],
						req.media['post_id'],
						1,
						req.media['content'],
						datetime.now(tz=timezone.utc),
					)
				)

			con.commit()

			resp.status = falcon.HTTP_200
			resp.media = 'Successful comment of post: {}'.format(req.media['post_id'])

		except psycopg2.DatabaseError as e:
			if con:
				con.rollback()
			print ('Error %s' % e )
			raise falcon.HTTPBadRequest('Database error', str(e))
		finally: 
			if cursor:
				cursor.close()
			if con:
				con.close()