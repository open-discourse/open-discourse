CREATE TABLE app_public.text_position__text
(
	id int8 NOT NULL,
	text_position int8 NOT NULL,
	speech_id int8 NOT NULL,
	"deleted_text" varchar NULL,
	CONSTRAINT text_position__text_pk PRIMARY KEY (id),
	CONSTRAINT text_position__text_fk FOREIGN KEY (speech_id) REFERENCES app_public.speeches(id)
);

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE app_public.text_position__text TO visitor;