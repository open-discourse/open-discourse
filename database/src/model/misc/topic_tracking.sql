CREATE TABLE misc.topic_tracking
(
	id bigserial NOT NULL,
	search_query text NOT NULL,
	"timestamp" TIMESTAMP DEFAULT now(),
	CONSTRAINT topic_tracking_pk PRIMARY KEY (id)
);

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE misc.topic_tracking TO visitor;
