CREATE TABLE misc.fts_tracking
(
	id bigserial NOT NULL,
	search_query text NOT NULL,
	"timestamp" TIMESTAMP DEFAULT now(),
	CONSTRAINT fts_tracking_pk PRIMARY KEY (id)
);

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE misc.fts_tracking TO visitor;
