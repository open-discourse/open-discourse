CREATE TABLE app_public.contributions_lookup
(
	id int8 NOT NULL,
	text_position int8 NOT NULL,
	speech_id int8 NOT NULL,
	"deleted_text" varchar NULL,
	CONSTRAINT contributions_lookup_pk PRIMARY KEY (id),
	CONSTRAINT contributions_lookup_fk FOREIGN KEY (speech_id) REFERENCES app_public.speeches(id)
);

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE app_public.contributions_lookup TO visitor;
