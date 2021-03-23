import falcon
import base64
import sys
import psycopg2.extras
from datetime import datetime, timezone
from falcon.http_status import HTTPStatus
from app.queries_new_schema import QUERY_CHECK_CONNECTION, QUERY_GET_REPORTED_POST, QUERY_UPDATE_REPORT_POST

class ReportPostService:
	def __init__(self, service):
		print('Initializing Report Post Service...')
		self.service = service

	def on_get(self, req, resp):
		print('HTTP GET: /report_post')
		print(req.params)
		
		self.service.dbconnection.init_db_connection()
		con = self.service.dbconnection.connection
		cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
		cursor.execute(QUERY_GET_REPORTED_POST, )
		
		response = []
		for record in cursor:
			if record[5] is None:
				latitude = 0.0
			else:
				latitude = record[5]
				
			if record[6] is None:
				longitude = 0.0
			else:
				longitude = record[6]
			response.append(
				{
					'id': record[0],
					'user_id': record[1],
					'category_id': record[2],
					'title': record[3],
					'content': record[4],
					'latitude': latitude,
					'longitude': longitude,
					'is_voted': record[7],
					'prev_vote': record[8],
					'date_created': str(record[9]),
					'comments': record[10],
					'votes': record[11],
					'username': record[12]
				}
			)
		
		cursor.close()
		con.close()
		print(response)
		resp.status = falcon.HTTP_200
		resp.media = response
		
	def on_post(self, req, resp):
		self.service.dbconnection.init_db_connection()
		con = self.service.dbconnection.connection
		
		try:
			print('HTTP POST: /report_post')
			print(req.media)
			
			cursor = con.cursor()
			cursor.execute(QUERY_UPDATE_REPORT_POST, (
				req.media['user_id'],
				req.media['content'],
				datetime.now(tz=timezone.utc),
				req.media['post_id'],
				req.media['post_id']
				)
			)
			con.commit()
			cursor.close()

			resp.status = falcon.HTTP_200
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