CREATE TABLE app_public.electoral_terms (
	id int8 NOT NULL,
	"start_date" int8 NOT NULL,
	"end_date" int8 NULL,
	CONSTRAINT electoral_terms_pk PRIMARY KEY (id)
);

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE app_public.electoral_terms TO visitor;
