routers = dict(
BASE = dict(
default_application='3muses'
)
)

routes_onerror=[
	('3muses/*', '/3muses/handle_error.html'),
	#'3muses/display/*', '/3muses/dne.html'),
]


