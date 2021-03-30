"""First revision

Revision ID: 9f0128c8efba
Revises: 
Create Date: 2021-03-29 04:24:40.311428

"""
import sqlalchemy as sa
import sqlalchemy_searchable as ss
from alembic import op
import mandarin.database.utils.ts as ts

# revision identifiers, used by Alembic.
revision = "9f0128c8efba"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()

    # Album

    op.create_table(
        "albums",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("search", ts.to_tsvector(
            a=["title"],
            b=["description"],
        ), nullable=True),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index("ix_albums_search", "albums", ["search"], unique=False, postgresql_using="gin")
    ss.sync_trigger(conn=conn, table_name="albums", tsvector_column="search", indexed_columns=["title", "description"])

    # Genre

    op.create_table(
        "genres",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("supergenre_id", sa.Integer(), nullable=True),
        sa.Column("search", ts.to_tsvector(
            a=["name"],
            b=["description"],
        ), nullable=True),
        sa.ForeignKeyConstraint(("supergenre_id",), ["genres.id"], ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name")
    )
    op.create_index("ix_genres_search", "genres", ["search"], unique=False, postgresql_using="gin")
    ss.sync_trigger(conn=conn, table_name="genres", tsvector_column="search", indexed_columns=["name", "description"])

    # Person

    op.create_table(
        "people",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("search", ts.to_tsvector(
            a=["name"],
            b=["description"],
        ), nullable=True),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index("ix_people_search", "people", ["search"], unique=False, postgresql_using="gin")
    ss.sync_trigger(conn=conn, table_name="people", tsvector_column="search", indexed_columns=["name", "description"])

    # Role

    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("search", ts.to_tsvector(
            a=["name"],
            b=["description"],
        ), nullable=True),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index("ix_roles_search", "roles", ["search"], unique=False, postgresql_using="gin")
    ss.sync_trigger(conn=conn, table_name="roles", tsvector_column="search", indexed_columns=["name", "description"])

    # User

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sub", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("nickname", sa.String(), nullable=False),
        sa.Column("picture", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("email_verified", sa.String(), nullable=False),
        sa.Column("updated_at", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id")
    )

    # AlbumGenre

    op.create_table(
        "albumgenres",
        sa.Column("album_id", sa.Integer(), nullable=False),
        sa.Column("genre_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(("album_id",), ["albums.id"], ),
        sa.ForeignKeyConstraint(("genre_id",), ["genres.id"], ),
        sa.PrimaryKeyConstraint("album_id", "genre_id")
    )

    # AlbumInvolvement

    op.create_table(
        "albuminvolvements",
        sa.Column("person_id", sa.Integer(), nullable=False),
        sa.Column("album_id", sa.Integer(), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(("album_id",), ["albums.id"], ),
        sa.ForeignKeyConstraint(("person_id",), ["people.id"], ),
        sa.ForeignKeyConstraint(("role_id",), ["roles.id"], ),
        sa.PrimaryKeyConstraint("person_id", "album_id", "role_id")
    )

    # AuditLog

    op.create_table(
        "auditlogs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("obj", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(("user_id",), ["users.id"], ),
        sa.PrimaryKeyConstraint("id")
    )

    # Song

    op.create_table(
        "songs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("lyrics", sa.Text(), nullable=False),
        sa.Column("disc", sa.Integer(), nullable=True),
        sa.Column("track", sa.Integer(), nullable=True),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("album_id", sa.Integer(), nullable=True),
        sa.Column("search", ts.to_tsvector(
            a=["title"],
            b=["description"],
            c=["lyrics"],
        ), nullable=True),
        sa.ForeignKeyConstraint(("album_id",), ["albums.id"], ),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index("ix_songs_search", "songs", ["search"], unique=False, postgresql_using="gin")
    ss.sync_trigger(
        conn=conn,
        table_name="songs",
        tsvector_column="search",
        indexed_columns=["title", "description", "lyrics"]
    )

    # Layer

    op.create_table(
        "layers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), server_default="Default", nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("song_id", sa.Integer(), nullable=True),
        sa.Column("search", ts.to_tsvector(
            a=["name"],
            b=["description"],
        ), nullable=True),
        sa.ForeignKeyConstraint(("song_id",), ["songs.id"], ),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index("ix_layers_search", "layers", ["search"], unique=False, postgresql_using="gin")
    ss.sync_trigger(conn=conn, table_name="layers", tsvector_column="search", indexed_columns=["name", "description"])

    # SongGenre

    op.create_table(
        "songgenres",
        sa.Column("song_id", sa.Integer(), nullable=False),
        sa.Column("genre_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(("genre_id",), ["genres.id"], ),
        sa.ForeignKeyConstraint(("song_id",), ["songs.id"], ),
        sa.PrimaryKeyConstraint("song_id", "genre_id")
    )

    # SongInvolvement

    op.create_table(
        "songinvolvements",
        sa.Column("person_id", sa.Integer(), nullable=False),
        sa.Column("song_id", sa.Integer(), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(("person_id",), ["people.id"], ),
        sa.ForeignKeyConstraint(("role_id",), ["roles.id"], ),
        sa.ForeignKeyConstraint(("song_id",), ["songs.id"], ),
        sa.PrimaryKeyConstraint("person_id", "song_id", "role_id")
    )

    # Encoding

    op.create_table(
        "encodings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("location", sa.String(), nullable=False),
        sa.Column("mime_type", sa.String(), nullable=True),
        sa.Column("mime_software", sa.String(), nullable=True),
        sa.Column("uploader_id", sa.Integer(), nullable=True),
        sa.Column("layer_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(("layer_id",), ["layers.id"], ),
        sa.ForeignKeyConstraint(("uploader_id",), ["users.id"], ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("location")
    )


def downgrade():
    conn = op.get_bind()

    op.drop_table("encodings")
    op.drop_table("songinvolvements")
    op.drop_table("songgenres")
    op.drop_index("ix_layers_search", table_name="layers")
    op.drop_table("layers")
    op.drop_index("ix_songs_search", table_name="songs")
    op.drop_table("songs")
    op.drop_table("auditlogs")
    op.drop_table("albuminvolvements")
    op.drop_table("albumgenres")
    op.drop_table("users")
    op.drop_index("ix_roles_search", table_name="roles")
    op.drop_table("roles")
    op.drop_index("ix_people_search", table_name="people")
    op.drop_table("people")
    op.drop_index("ix_genres_search", table_name="genres")
    op.drop_table("genres")
    op.drop_index("ix_albums_search", table_name="albums")
    op.drop_table("albums")

    ss.sync_trigger(conn=conn, table_name="albums", tsvector_column="search", indexed_columns=["title", "description"])
    ss.sync_trigger(conn=conn, table_name="genres", tsvector_column="search", indexed_columns=["name", "description"])
    ss.sync_trigger(conn=conn, table_name="people", tsvector_column="search", indexed_columns=["name", "description"])
    ss.sync_trigger(conn=conn, table_name="roles", tsvector_column="search", indexed_columns=["name", "description"])
    ss.sync_trigger(
        conn=conn,
        table_name="songs",
        tsvector_column="search",
        indexed_columns=["title", "description", "lyrics"]
    )
    ss.sync_trigger(conn=conn, table_name="layers", tsvector_column="search", indexed_columns=["name", "description"])
