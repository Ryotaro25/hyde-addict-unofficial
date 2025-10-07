DROP TABLE IF EXISTS tb_member;
DROP TABLE IF EXISTS tb_artist;
DROP TABLE IF EXISTS tb_magazine;
DROP TABLE IF EXISTS tb_publish;
DROP TABLE IF EXISTS tb_performance;
DROP TABLE IF EXISTS tb_book;
DROP TABLE IF EXISTS tb_song;
DROP TABLE IF EXISTS tb_release;
DROP TABLE IF EXISTS tb_track;

CREATE TABLE "tb_member" (
  "member_id" INTEGER UNIQUE,
  "member_name" TEXT,
  "birthdate" TEXT,
  PRIMARY KEY("member_id" AUTOINCREMENT)
);

CREATE TABLE "tb_artist" (
  "artist_id" INTEGER UNIQUE,
  "artist_name" TEXT,
  PRIMARY KEY("artist_id" AUTOINCREMENT)
);

CREATE TABLE "tb_magazine" (
  "magazine_id" INTEGER UNIQUE,
  "magazine_name" TEXT,
  "publisher_name" TEXT,
  PRIMARY KEY("magazine_id" AUTOINCREMENT)
);

CREATE TABLE "tb_publish" (
  "publish_id" INTEGER UNIQUE,
  "magazine_id" INTEGER,
  "artist_id" INTEGER,
  "publish_date" TEXT,
  "is_possess" TEXT,
  PRIMARY KEY("publish_id" AUTOINCREMENT)
);

CREATE TABLE "tb_performance" (
  "performance_id" INTEGER UNIQUE,
  "artist_id" INTEGER,
  "live_name" TEXT,
  "live_place" TEXT,
  "live_date" TEXT,
  PRIMARY KEY("performance_id" AUTOINCREMENT)
);

CREATE TABLE "tb_book" (
  "book_id" INTEGER UNIQUE,
  "artist_id" INTEGER,
  "book_name" TEXT,
  "publisher_name" TEXT,
  "publish_date" TEXT,
  "is_possess" TEXT,
  PRIMARY KEY("book_id" AUTOINCREMENT)
);

CREATE TABLE "tb_release" (
  "release_id" INTEGER UNIQUE,
  "artist_id" INTEGER,
  "release_name" TEXT,
  "release_type" TEXT, -- single, album, best, live-album, video
  "only_digital" TEXT,
  "release_date" TEXT,
  PRIMARY KEY("release_id" AUTOINCREMENT)
);

CREATE TABLE "tb_song" (
  "song_id" INTEGER UNIQUE,
  "song_name" TEXT,
  "lyricist" TEXT,
  "composer" TEXT,
  "duratetion_second" INTEGER,
  "bpm" REAL,
  PRIMARY KEY("song_id" AUTOINCREMENT)
);

CREATE TABLE "tb_track" (
  "release_id" INTEGER,
  "song_id" INTEGER,
  "track_number" INTEGER
);
