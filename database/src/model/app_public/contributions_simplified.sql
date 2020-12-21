CREATE TABLE app_public.contributions_simplified
(
	id int8 NOT NULL,
	text_position int8 NOT NULL,
	speech_id int8 NOT NULL,
	content varchar NULL,
	CONSTRAINT contributions_simplified_pk PRIMARY KEY (id),
	CONSTRAINT contributions_simplified_fk FOREIGN KEY (speech_id) REFERENCES app_public.speeches(id)
);

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE app_public.contributions_simplified TO visitor;
