CREATE TABLE user_profile (
	user_id SERIAL,
	user_email VARCHAR(255) NOT NULL,
	user_name VARCHAR(255) DEFAULT NULL,
	login_token VARCHAR(255) NOT NULL,
	profile_img BYTEA DEFAULT NULL,
	gender VARCHAR(20) DEFAULT NULL,
	birthday VARCHAR(20) DEFAULT NULL,
	date_added TIMESTAMP WITH TIME ZONE DEFAULT NULL,
	date_modified TIMESTAMP WITH TIME ZONE DEFAULT NULL,
	PRIMARY KEY (user_id)
);



CREATE TABLE chat_list (
	user_id BIGINT NOT NULL,
	chat_id integer[] DEFAULT NULL,
	date_added TIMESTAMP WITH TIME ZONE DEFAULT NULL,
	date_modified TIMESTAMP WITH TIME ZONE DEFAULT NULL,
	PRIMARY KEY (user_id)
);

CREATE TABLE contact_list (
	user_id BIGINT NOT NULL,
	friend_id integer[] DEFAULT NULL,
	date_added TIMESTAMP WITH TIME ZONE DEFAULT NULL,
	date_modified TIMESTAMP WITH TIME ZONE DEFAULT NULL,
	PRIMARY KEY (user_id)
);

CREATE TABLE chat_members (
	chat_id SERIAL,
	member_id bigint[] DEFAULT NULL,
	date_added TIMESTAMP WITHOUT TIME ZONE DEFAULT NULL,
	date_modified TIMESTAMP WITHOUT TIME ZONE DEFAULT NULL,
	PRIMARY KEY (chat_id)
);

CREATE TABLE friend_token (
	user_id BIGINT NOT NULL,
	token BIGINT DEFAULT NULL,
	date_added TIMESTAMP WITH TIME ZONE DEFAULT NULL,
	PRIMARY KEY (user_id)
);


create table chat (
	id SERIAL,
	chat_id text not null,
	user_id BIGINT not null,
	user_name text DEFAULT null,
	user_email text not null,
	message text DEFAULT null,
	media bytea DEFAULT null,
	message_type integer DEFAULT 0,
	date_added TIMESTAMP WITHOUT TIME ZONE DEFAULT NULL,
	date_modified TIMESTAMP WITHOUT TIME ZONE DEFAULT NULL,
	PRIMARY KEY (id)	
);


