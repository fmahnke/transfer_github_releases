import json
from StringIO import StringIO
from octohub.connection import Connection
import requests

# Source repository
GITHUB_COM_OAUTH_TOKEN = "token" # https://github.com/settings/applications#personal-access-tokens
GITHUB_COM_REPOSITORY = "org/repo"

# Destination repository
ENTERPRISE_OAUTH_TOKEN = "other token"
ENTERPRISE_REPOSITORY = "org/repo"
ENTERPRISE_URL = "https://your.enterprise.github/api/v3"

class Repository:
	def __init__(self, token, repository, api_url=None):
		self.token = token
		self.repository = repository
		self.api_url = api_url
		self._connect()

	def _connect(self):
		self.connection = Connection(self.token)
		if self.api_url:
			self.connection.endpoint = self.api_url

	def fetch_releases(self):
		uri = '/repos/{}/releases'.format(self.repository)
		response = self.connection.send('GET', uri)
		return response

	def create_release(self, data):
		uri = '/repos/{}/releases'.format(self.repository)
		response = self.connection.send('POST', uri, data=json.dumps(data))
		return response

	def edit_release(self, release_id, data):
		uri = '/repos/{}/releases/{}'.format(self.repository, release_id)
		response = self.connection.send('PATCH', uri, data=json.dumps(data))
		return response

	def delete_release(self, release_id):
		uri = '/repos/{}/releases/{}'.format(self.repository, release_id)
		response = self.connection.send('DELETE', uri)
		assert response.status_code == 204
		return response

	def download_asset(self, uri):
		headers = dict()
		headers["Authorization"] = "token " + self.token
		headers["Accept"] = "application/octet-stream"
		r = requests.get(uri, stream=True, headers=headers)
		assert r.status_code == 200
		asset_binary = StringIO()
		for chunk in r.iter_content(1024):
			asset_binary.write(chunk)
		return asset_binary

	def upload_asset(self, uri, filename, content_type, data):
		headers = dict()
		headers["Authorization"] = "token " + self.token
		headers["Content-Type"] = content_type
		r = requests.post(uri, params={'name': filename}, headers=headers, data=data, timeout=1)
		assert r.status_code == 201
		return r

if __name__ == "__main__":
	source_repo = Repository(GITHUB_COM_OAUTH_TOKEN, GITHUB_COM_REPOSITORY)
	target_repo = Repository(ENTERPRISE_OAUTH_TOKEN, ENTERPRISE_REPOSITORY, ENTERPRISE_URL)

	try:
		target_releases = target_repo.fetch_releases()
		existing_releases_map = dict()
		for release in target_releases.parsed:
			existing_releases_map[release.tag_name] = release.id
	except AttributeError:
		# workaround for bug in octohub
		existing_releases_map = dict()

	source_releases = source_repo.fetch_releases()
	for release in source_releases.parsed:
		print "Release #{}: [{}] {}".format(release.id, release.tag_name, release.name)

		# copy data for release creation
		new_release = dict()
		for key in ["tag_name", "target_commitish", "name", "body", "draft", "prerelease"]:
			new_release[key] = release[key]

		# if the release already exists in destination, delete it first
		if existing_releases_map.get(release.tag_name):
			print "[-] apparently already exists as #{}, skipping it...".format(existing_releases_map.get(release.tag_name))
			continue # remove this line to delete existing releases instead
			target_repo.delete_release(existing_releases_map.get(release.tag_name))
			del existing_releases_map[release.tag_name]

		# create release in destination
		create_release_response = target_repo.create_release(new_release)
		new_release_id = create_release_response.parsed.id
		upload_url = create_release_response.parsed.upload_url.replace("{?name}","")
		print "`-----> #{}".format(new_release_id)

		# check for assets and download them
		for asset in release.assets:
			print "        Downloading asset {}.".format(asset.name)
			asset_binary = source_repo.download_asset(asset.url)
			print "        `- Downloaded {} kB. Starting upload.".format(asset_binary.len / 1024)
			upload = target_repo.upload_asset(upload_url, asset.name, asset.content_type, asset_binary.getvalue())
			print "        `- Successfully uploaded asset."
			asset_binary.close() # free memory

	print "Transferred all releases."

