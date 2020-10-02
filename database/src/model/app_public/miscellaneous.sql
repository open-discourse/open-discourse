CREATE TABLE app_public.miscellaneous (
	id int8 NOT NULL,
	speech_id int8 NOT NULL,
	"content" varchar NULL,
	"text_position" int8 NOT NULL,
	CONSTRAINT miscellaneous_pk PRIMARY KEY (id),
	CONSTRAINT miscellaneous_fk FOREIGN KEY (speech_id) REFERENCES app_public.speeches(id)
);

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE app_public.miscellaneous TO visitor;