import sqlite3
import os
from time import time
from random import randint
from data.classes.utils import is_viable_color
from .tag import Tag
from .flashcard import Flashcard
from .box import Box
from data.classes.utils import a_difference_b
from datetime import datetime


class FlashcardDataBase:

    """
    Class created to handle database and almost entirely separate sql-related code from app's one.
    All methods are static to maintain style from app-wide functionalities like Cache, Config etc.
    Important returned values from 'insert' functions:
        ColorError - when is_viable_color function returns False
        LengthError - reparation of sql problem with sticking to fixed binary data lengths, raised when passed string is too long
        NameError - when unique constraint is being breached
    """

    @staticmethod
    def get_grouped_texts(database: str) -> list:
        if not os.path.isfile(database):
            FlashcardDataBase.create_database(database)

        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()

            get_ids_q = """
                SELECT id FROM cards;
            """
            card_ids = FlashcardDataBase.normalize_result(cursor.execute(get_ids_q).fetchall())

            get_texts_q = """
                SELECT text FROM content_lines WHERE card_id = ?;
            """

            groups = []
            for card_id in card_ids:
                result = cursor.execute(get_texts_q, (card_id,)).fetchall()
                groups.append(tuple(item[0] for item in result))

        return groups

    @staticmethod
    def normalize_result(result: list) -> list:
        if not result:
            return result
        else:
            normalized = []
            columns_nmb = len(result[0])

            for i in range(columns_nmb):
                tuple_to_list = []
                for res_tuple in result:
                    tuple_to_list.append(res_tuple[i])
                normalized.append(tuple_to_list)

            return normalized if columns_nmb > 1 else normalized[0]

    """
    In this method flashcards are to be searched in original database, though they come from auxiliary one. 
    Therefore equality_index equal to 1 is enough to mark card as redundant.
    """
    @staticmethod
    def mark_redundant(database: str, flashcards: list):
        if not os.path.isfile(database):
            FlashcardDataBase.create_database(database)

        groups = FlashcardDataBase.get_grouped_texts(database)

        for flashcard in flashcards:
            encoded_lines = tuple(line.encode(encoding="UTF-8", errors="replace") for line in flashcard.def_lines) \
                            + tuple(line.encode(encoding="UTF-8", errors="replace") for line in flashcard.hidden_lines)

            equality_index = 0
            for group in groups:
                if not a_difference_b(encoded_lines, group) and not a_difference_b(group, encoded_lines):
                    equality_index += 1

            flashcard.dev_tag = "redundant" if equality_index > 0 else None

    @staticmethod
    def upload_backup(filename: str) -> dict:

        if not os.path.isfile(filename):
            print("aaaa")

        with open(filename, "r", encoding="utf-8") as file:
            cards_info, tags_info, boxes_info = [], [], []
            content_lines_info, cards_in_tags_info, cards_in_boxes_info = [], [], []

            cards_nr = int(file.readline().rstrip())
            for i in range(cards_nr):
                cards_info.append(tuple(file.readline().strip().split("\t")))

            print(cards_info)

    @staticmethod
    def save_backup(database: str, directory: str):
        if not os.path.isfile(database):
            FlashcardDataBase.create_database(database)

        filename = datetime.fromtimestamp(int(time())).strftime("ottercards_backup_%Y%m%d%H%M.ocb")

        new_filepath = os.path.join(directory, filename)

        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()

            cards_q = """
                    SELECT * FROM cards;
            """
            cards_info = cursor.execute(cards_q).fetchall()

            boxes_q = """
                    SELECT * FROM boxes;
            """
            boxes_info = cursor.execute(boxes_q).fetchall()

            tags_q = """
                    SELECT * FROM tags;
            """
            tags_info = cursor.execute(tags_q).fetchall()

            content_lines_q = """
                    SELECT * FROM content_lines;
            """
            content_lines_info = cursor.execute(content_lines_q).fetchall()

            cards_in_tags_q = """
                    SELECT * FROM cards_in_tags;
            """
            cards_in_tags_info = cursor.execute(cards_in_tags_q).fetchall()

            cards_in_boxes_q = """
                    SELECT * FROM cards_in_boxes;
            """
            cards_in_boxes_info = cursor.execute(cards_in_boxes_q).fetchall()

        with open(new_filepath, "wb") as file:

            file.write(f"{len(cards_info)}\n".encode("utf-8"))
            for card_id, last_update in cards_info:
                file.write(f"{card_id}\t{last_update}\n".encode("utf-8"))

            file.write(f"{len(boxes_info)}\n".encode("utf-8"))
            for box_id, name, color, nr_compartments, creation_date, last_update, special, cards_left in boxes_info:
                file.write(f"{box_id}\t{color}\t{nr_compartments}\t{creation_date}\t{last_update}\t{special}\t{cards_left}\n{name}\n".encode("utf-8"))

            file.write(f"{len(tags_info)}\n".encode("utf-8"))
            for tag_id, name, color, last_update in tags_info:
                file.write(f"{tag_id}\t{color}\t{last_update}\n{name}\n".encode("utf-8"))

            file.write(f"{len(content_lines_info)}\n".encode("utf-8"))
            for text, is_def, card_id in content_lines_info:
                file.write(f"{card_id}\t{is_def}\n{text}\n".encode("utf-8"))

            file.write(f"{len(cards_in_boxes_info)}\n".encode("utf-8"))
            for card_id, box_id, comp_nr in cards_in_boxes_info:
                file.write(f"{card_id}\t{box_id}\t{comp_nr}\n".encode("utf-8"))

            file.write(f"{len(cards_in_tags_info)}\n".encode("utf-8"))
            for card_id, tag_id in cards_in_tags_info:
                file.write(f"{card_id}\t{tag_id}\n".encode("utf-8"))

    @staticmethod
    def strip_box(database: str, box_id: int, flashcards: list):
        if not os.path.isfile(database):
            FlashcardDataBase.create_database(database)

        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()

            for flashcard in flashcards:
                strip_box_q = """
                        DELETE FROM cards_in_boxes WHERE box_id = ? AND card_id = ?;
                """
                args = (box_id, flashcard.id)

                cursor.execute(strip_box_q, args)

                last_update_q = """
                        UPDATE cards SET last_update = ? WHERE id = ?;
                """
                args = (int(time()), flashcard.id)

                cursor.execute(last_update_q, args)

            connection.commit()

    @staticmethod
    def strip_tags(database: str, tagname: str, flashcards: list):
        if not os.path.isfile(database):
            FlashcardDataBase.create_database(database)

        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()

            get_tag_id_q = """
                SELECT id FROM tags WHERE name = ?;
            """
            args = (tagname.encode(encoding="utf-8", errors="replace"),)

            tag_id = FlashcardDataBase.normalize_result(cursor.execute(get_tag_id_q, args).fetchall())[0]

            for flashcard in flashcards:
                strip_tags_q = """
                    DELETE FROM cards_in_tags WHERE tag_id = ? AND card_id = ?;
                """
                args = (tag_id, flashcard.id)

                cursor.execute(strip_tags_q, args)

                last_update_q = """UPDATE cards SET last_update = ? WHERE id = ?;"""
                args = (int(time()), flashcard.id)

                cursor.execute(last_update_q, args)

            connection.commit()

    @staticmethod
    def delete_boxes(database: str, boxes: list):
        if not os.path.isfile(database):
            FlashcardDataBase.create_database(database)

        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()

            cards_changed_ids = []

            for box in boxes:

                delete_box_q = """
                    DELETE FROM boxes WHERE id = ?;
                """
                args = (box.id, )
                cursor.execute(delete_box_q, args)

                get_card_ids_q = """
                    SELECT card_id FROM cards_in_boxes WHERE box_id = ?;
                """
                args = (box.id,)

                card_ids = FlashcardDataBase.normalize_result(cursor.execute(get_card_ids_q, args).fetchall())
                cards_changed_ids += card_ids

                delete_cards_in_boxes_q = """
                    DELETE from cards_in_boxes WHERE box_id = ?;
                """
                args = (box.id,)
                cursor.execute(delete_cards_in_boxes_q, args)

            cards_changed_ids = list(set(cards_changed_ids))

            last_update_q = """
                UPDATE cards SET last_update = ? WHERE id IN ({seq});
            """.format(seq=",".join(["?"] * len(cards_changed_ids)))
            args = (int(time()),) + tuple(cards_changed_ids)
            cursor.execute(last_update_q, args)

            connection.commit()

    @staticmethod
    def delete_cards(database: str, flashcards: list):
        if not os.path.isfile(database):
            FlashcardDataBase.create_database(database)

        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()

            for flashcard in flashcards:
                delete_card_q = """
                    DELETE FROM cards WHERE id = ?;
                """
                args = (flashcard.id, )

                cursor.execute(delete_card_q, args)

                delete_lines_q = """
                    DELETE FROM content_lines WHERE card_id = ?;
                """
                args = (flashcard.id, )

                cursor.execute(delete_lines_q, args)

                delete_relations_q = """
                    DELETE FROM cards_in_tags WHERE card_id = ?;
                """
                args = (flashcard.id, )

                cursor.execute(delete_relations_q, args)

                delete_relations_q = """
                    DELETE FROM cards_in_boxes WHERE card_id = ?;
                """
                args = (flashcard.id, )

                cursor.execute(delete_relations_q, args)

            connection.commit()

    @staticmethod
    def delete_tag(database: str, tag: Tag):
        if not os.path.isfile(database):
            FlashcardDataBase.create_database(database)

        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()

            delete_tag_q = """
                DELETE FROM tags WHERE id = ?;
            """
            args = (tag.id,)

            cursor.execute(delete_tag_q, args)

            get_card_ids_q = """
                SELECT card_id FROM cards_in_tags WHERE tag_id = ?;
            """
            args = (tag.id, )

            ids_to_update = FlashcardDataBase.normalize_result(cursor.execute(get_card_ids_q, args).fetchall())
            update_cards_q = """
                        UPDATE cards SET last_update = ? WHERE id IN ({seq});
                    """.format(seq=",".join(["?"] * len(ids_to_update)))

            args = (int(time()),) + tuple(ids_to_update)
            cursor.execute(update_cards_q, args)

            delete_relations_q = """
                DELETE FROM cards_in_tags WHERE tag_id = ?;
            """
            args = (tag.id,)

            cursor.execute(delete_relations_q, args)

            connection.commit()

    @staticmethod
    def retrieve_tags(database: str, **kwargs) -> list:
        if not os.path.isfile(database):
            FlashcardDataBase.create_database(database)

        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()
            connection.text_factory = bytes

            names = kwargs.get("names", None)
            not_names = kwargs.get("not_names", None)

            if names is None and not_names is None:
                get_tags_q = """
                    SELECT name, id, color, last_update FROM tags;
                """
                tags_info = cursor.execute(get_tags_q).fetchall()
            else:
                negation_prefix = "NOT" if names is None else ""  # 'not' word used to get matching or not matching tags
                names = names if not_names is None else not_names   # just to avoid additional conditionals

                for i in range(len(names)):
                    names[i] = names[i].encode(encoding="UTF-8", errors="replace")

                get_tags_q = """
                                SELECT name, id, color, last_update FROM tags WHERE name {neg} IN ({seq});
                            """.format(seq=",".join(["?"]*len(names)), neg=negation_prefix)
                tags_info = cursor.execute(get_tags_q, tuple(names)).fetchall()

            tags = []
            for name, tag_id, color, last_update in tags_info:
                tags.append(Tag(tag_id, name.decode(encoding="UTF-8", errors="replace"),
                                color.decode(encoding="UTF-8", errors="replace"), last_update))

        return tags

    @staticmethod
    def retrieve_boxes(database: str) -> list:
        if not os.path.isfile(database):
            FlashcardDataBase.create_database(database)

        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()

            get_boxes_q = """
                SELECT id, name, nr_compartments, last_update, color, special, cards_left, creation_date FROM boxes;
            """
            boxes_info = FlashcardDataBase.normalize_result(cursor.execute(get_boxes_q).fetchall())

            if not boxes_info:
                return boxes_info

            box_ids, names, nrs_comp = boxes_info[0], boxes_info[1], boxes_info[2]
            update_dates, colors, specials = boxes_info[3], boxes_info[4], boxes_info[5]
            cards_lefts, creation_dates = boxes_info[6], boxes_info[7]

            boxes = []
            for box_id, name, nr_compartments, last_update, color, special, cards_left, creation_date in \
                    zip(box_ids, names, nrs_comp, update_dates, colors, specials, cards_lefts, creation_dates):

                name = name.decode(encoding="UTF-8", errors="replace")

                get_cards_nr_q = """
                    SELECT COUNT(card_id) FROM cards_in_boxes WHERE box_id = ?;
                """
                args = (box_id,)
                nr_cards = FlashcardDataBase.normalize_result(cursor.execute(get_cards_nr_q, args).fetchall())[0]

                boxes.append(Box(id=box_id, name=name, nr_compartments=nr_compartments,
                                 last_update=last_update, color=color, nr_cards=nr_cards, is_special=bool(special),
                                 cards_left=cards_left, creation_date=creation_date))

        return boxes

    @staticmethod
    def retrieve_cards(database: str, mode: str, **kwargs) -> list:
        if not os.path.isfile(database):
            FlashcardDataBase.create_database(database)

        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()

            limit = kwargs.get("limit", None)
            not_ids = kwargs.get("not_ids", [])

            # /////// preparing ids depending on mode ////////////
            if mode == "all":
                get_all_ids_q = """
                    SELECT id FROM cards;
                """
                card_ids = FlashcardDataBase.normalize_result(cursor.execute(get_all_ids_q).fetchall())

            elif mode == "tag":
                tagname = kwargs["tag"]

                get_having_tag_q = """
                    SELECT cards_in_tags.card_id 
                    FROM cards_in_tags
                    INNER JOIN tags on cards_in_tags.tag_id = tags.id
                    WHERE tags.name = ?;
                """
                args = (tagname.encode(encoding="UTF-8", errors="replace"),)
                card_ids = FlashcardDataBase.normalize_result(cursor.execute(get_having_tag_q, args).fetchall())

            elif mode == "box":
                box_id = kwargs["box"]
                comp_nr = kwargs["compartment"]

                get_by_box_comp_q = """
                    SELECT card_id FROM cards_in_boxes WHERE box_id = ? AND comp_nr = ?;
                """
                args = (box_id, comp_nr)
                card_ids = FlashcardDataBase.normalize_result(cursor.execute(get_by_box_comp_q, args).fetchall())
            
            elif mode == "id":
                card_ids = kwargs["ids"]

            card_ids = a_difference_b(card_ids, not_ids)
            if limit is not None and len(card_ids) >= limit:
                card_ids = card_ids[:limit]

            # /////////////////////////////////////////////////////

            flashcards = []
            for card_id in card_ids:
                get_lastupdate_q = """
                                SELECT last_update FROM cards WHERE id = ?;
                            """
                args = (card_id,)
                last_update = FlashcardDataBase.normalize_result(cursor.execute(get_lastupdate_q, args).fetchall())
                if last_update:
                    last_update = last_update[0]

                get_tagnames_q = """
                                SELECT tags.name
                                FROM cards_in_tags
                                INNER JOIN tags ON cards_in_tags.tag_id = tags.id
                                WHERE cards_in_tags.card_id = ?;
                            """
                args = (card_id,)
                tags = FlashcardDataBase.normalize_result(cursor.execute(get_tagnames_q, args).fetchall())
                tags = [tag.decode(encoding="UTF-8", errors="replace") for tag in tags]

                get_def_q = """
                                SELECT text FROM content_lines WHERE card_id = ? AND is_def = ?;
                            """
                args = (card_id, True)
                defl = FlashcardDataBase.normalize_result(cursor.execute(get_def_q, args).fetchall())
                defl = [l.decode(encoding="UTF-8", errors="replace") for l in defl]

                get_hidden_q = """
                                SELECT text FROM content_lines WHERE card_id = ? AND is_def = ?;
                            """
                args = (card_id, False)
                hiddenl = FlashcardDataBase.normalize_result(cursor.execute(get_hidden_q, args).fetchall())
                hiddenl = [l.decode(encoding="UTF-8", errors="replace") for l in hiddenl]

                flashcards.append(Flashcard(
                    id=card_id, tags=tags, def_lines=defl,
                    hidden_lines=hiddenl, last_update=last_update))

            connection.commit()

        return flashcards

    """
    A method to shift cards in box. comp_nr argument means current compartment, if you're inserting card then pass None
    """
    @staticmethod
    def update_compartment(database: str, box_id, flashcards: list, comp_nr):
        if not os.path.isfile(database):
            FlashcardDataBase.create_database(database)

        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()

            cards_left_count = 0

            for flashcard in flashcards:

                # what if the card is not present in this box
                if comp_nr is None:

                    add_card_to_box_q = """
                        INSERT INTO cards_in_boxes (box_id, card_id, comp_nr) VALUES (?, ?, 1);
                    """
                    args = (box_id, flashcard.id)
                    cursor.execute(add_card_to_box_q, args)

                else:

                    get_nr_comps_q = """
                        SELECT nr_compartments FROM boxes WHERE id = ?;
                    """
                    args = (box_id,)

                    nr_comps = FlashcardDataBase.normalize_result(cursor.execute(get_nr_comps_q, args).fetchall())[0]

                    if comp_nr == nr_comps:
                        delete_from_box_q = """
                            DELETE FROM cards_in_boxes WHERE box_id = ? AND card_id = ?;
                        """
                        args = (box_id, flashcard.id)
                        cursor.execute(delete_from_box_q, args)

                        cards_left_count += 1

                    else:
                        shift_card_q = """
                            UPDATE cards_in_boxes SET comp_nr = ? WHERE card_id = ? AND box_id = ?;
                        """
                        args = (comp_nr + 1, flashcard.id, box_id)
                        cursor.execute(shift_card_q, args)

            box_update_q = "UPDATE boxes SET last_update = ?, cards_left = cards_left + ? WHERE id = ?;"
            args = (int(time()), cards_left_count, box_id)

            cursor.execute(box_update_q, args)
            connection.commit()

    @staticmethod
    def insert_box(database: str, box: Box):
        if not os.path.isfile(database):
            FlashcardDataBase.create_database(database)

        comp_nr = box.nr_compartments
        color = box.color
        box_id = box.id
        name = box.name.encode(encoding="UTF-8", errors="replace")
        is_special = box.is_special

        color = "ffffff" if color is None else color
        if not is_viable_color(color):
            return "ColorError"

        if len(name) > 150 or len(name) == 0:
            return "LengthError"

        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()
            connection.text_factory = bytes

            if box_id is None:

                get_box_ids_q = """
                    SELECT id FROM boxes;
                """
                box_ids = FlashcardDataBase.normalize_result(cursor.execute(get_box_ids_q).fetchall())

                unique_id = 1
                while unique_id in box_ids:
                    unique_id += 1

                get_boxes_same_name_count_q = """
                    SELECT count(name) FROM boxes where name = ?;
                """
                args = (name,)

                same_name_count = FlashcardDataBase.normalize_result(
                    cursor.execute(get_boxes_same_name_count_q, args).fetchall())[0]

                # information that insertion fell through because existing name has been passed
                if same_name_count != 0:
                    return "NameError"

                creation_date = int(time())

                last_update = creation_date

                insert_box_q = """
                    INSERT INTO boxes (id, name, color, nr_compartments, creation_date, last_update, cards_left, special) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """
                args = (unique_id, name, color, comp_nr, creation_date, last_update, 0, is_special)

                cursor.execute(insert_box_q, args)

            else:

                delete_above_comp_nr_q = """
                    DELETE FROM cards_in_boxes WHERE box_id = ? AND comp_nr > ?; 
                """
                args = (box_id, comp_nr)
                cursor.execute(delete_above_comp_nr_q, args)

                update_box_q = """
                    UPDATE boxes SET name = ?, color = ?, nr_compartments = ?, last_update = ? WHERE id = ?;
                """
                args = (name, color, comp_nr, int(time()), box_id)
                cursor.execute(update_box_q, args)

            connection.commit()

    @staticmethod
    def insert_tag(database: str, tag: Tag):
        if not os.path.isfile(database):
            FlashcardDataBase.create_database(database)

        name = tag.name.encode(encoding="UTF-8", errors="replace")
        tag_id = tag.id
        color = tag.color
        if not is_viable_color(color):
            return "ColorError"

        if len(name) > 150 or len(name) == 0:
            return "LengthError"

        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()

            if tag_id is None:
                get_tagnames_q = """
                    SELECT name FROM tags;
                """
                tagnames = FlashcardDataBase.normalize_result(cursor.execute(get_tagnames_q).fetchall())

                if name in tagnames:
                    return "NameError"

                tag_ids_q = """
                    SELECT id FROM tags;    
                """
                tag_ids = FlashcardDataBase.normalize_result(cursor.execute(tag_ids_q).fetchall())

                # setting unique id for new tag
                unique_tag_id = 1
                while unique_tag_id in tag_ids:
                    unique_tag_id += 1

                insert_tag_q = """
                    INSERT INTO tags (id, name, color, last_update) VALUES (?, ?, ?, ?);
                """
                args = (unique_tag_id, name, color, int(time()))
                cursor.execute(insert_tag_q, args)

            else:
                update_tag_q = """
                    UPDATE tags set name = ?, color = ?, last_update = ? WHERE id = ?;
                """
                args = (name, color, int(time()), tag_id)
                cursor.execute(update_tag_q, args)

            connection.commit()

    @staticmethod
    def insert_cards(database: str, flashcards: list):
        if not os.path.isfile(database):
            FlashcardDataBase.create_database(database)

        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()

            for flashcard in flashcards:

                for line in flashcard.hidden_lines + flashcard.def_lines:
                    if len(line.encode(encoding="utf-8", errors="replace")) > 1000:
                        return "LengthError"

                if flashcard.id is None:
                    get_ids_q = """
                        SELECT id FROM cards ORDER BY id DESC;
                    """
                    ids = FlashcardDataBase.normalize_result(cursor.execute(get_ids_q).fetchall())

                    # trying to find the lowest number that isn't taken by another card in database
                    unique_id = 1
                    while unique_id in ids:
                        unique_id += 1

                    last_update = int(time())

                    insert_card_q = """
                        INSERT INTO cards (id, last_update) VALUES (?, ?);
                    """
                    args = (unique_id, last_update)
                    cursor.execute(insert_card_q, args)

                    for line in flashcard.hidden_lines:
                        text = line.encode(encoding="UTF-8", errors="replace")
                        is_def = False
                        insert_content_q = """
                            INSERT INTO content_lines (card_id, is_def, text) VALUES (?, ?, ?);
                        """
                        args = (unique_id, is_def, text)
                        cursor.execute(insert_content_q, args)

                    for line in flashcard.def_lines:
                        text = line.encode(encoding="UTF-8", errors="replace")
                        is_def = True
                        insert_content_q = """
                            INSERT INTO content_lines (card_id, is_def, text) VALUES (?, ?, ?);
                        """
                        args = (unique_id, is_def, text)
                        cursor.execute(insert_content_q, args)

                    flashcard.id = unique_id    # needed when updating cards_in_tags table - flashcard is no longer new

                else:

                    last_update_q = "UPDATE cards SET last_update = ? WHERE id = ?;"
                    args = (int(time()), flashcard.id)

                    cursor.execute(last_update_q, args)

                    connection.text_factory = bytes
                    # ///// upload hidden lines
                    get_hidden_q = """
                        SELECT text FROM content_lines WHERE card_id = ? AND is_def = ?;
                    """
                    args = (flashcard.id, False)
                    old_hidden = FlashcardDataBase.normalize_result(cursor.execute(get_hidden_q, args).fetchall())

                    new_hidden = [line.encode(encoding="UTF-8", errors="replace") for line in flashcard.hidden_lines]

                    for old in old_hidden:
                        if old not in new_hidden:
                            delete_content_q = """
                                DELETE FROM content_lines WHERE card_id = ? AND text = ?;
                            """
                            args = (flashcard.id, old)
                            cursor.execute(delete_content_q, args)

                    for new in new_hidden:
                        if new not in old_hidden:
                            insert_content_q = """
                                INSERT INTO content_lines (card_id, is_def, text) VALUES (?, ?, ?);
                            """
                            args = (flashcard.id, False, new)
                            cursor.execute(insert_content_q, args)
                    # //////////////////////////

                    # ///// upload def lines /////////
                    get_def_q = """
                                    SELECT text FROM content_lines WHERE card_id = ? AND is_def = ?;
                                """
                    args = (flashcard.id, True)
                    old_def = FlashcardDataBase.normalize_result(cursor.execute(get_def_q, args).fetchall())

                    new_def = [line.encode(encoding="UTF-8", errors="replace") for line in flashcard.def_lines]

                    for old in old_def:
                        if old not in new_def:
                            delete_content_q = """
                                            DELETE FROM content_lines WHERE card_id = ? AND text = ?;
                                        """
                            args = (flashcard.id, old)
                            cursor.execute(delete_content_q, args)

                    for new in new_def:
                        if new not in old_def:
                            insert_content_q = """
                                            INSERT INTO content_lines (card_id, is_def, text) VALUES (?, ?, ?);
                                        """
                            args = (flashcard.id, True, new)
                            cursor.execute(insert_content_q, args)
                    # /////////////////////////////////

            connection.commit()

        # checking if there are tags to insert into database
        get_tags_q = """
                    SELECT name FROM tags;
                """
        tags = FlashcardDataBase.normalize_result(cursor.execute(get_tags_q).fetchall())

        for flashcard in flashcards:
            for tag in flashcard.tags:
                if tag.encode(encoding="UTF-8", errors="replace") not in tags:
                    rgb = [hex(randint(0, 255)).replace("0x", "") for i in range(3)]
                    rgb = "{}{}{}".format(rgb[0], rgb[1], rgb[2])

                    FlashcardDataBase.insert_tag(database, Tag(None, tag, rgb))

        with sqlite3.connect(database) as connection:
            for flashcard in flashcards:
                cursor = connection.cursor()

                get_tag_ids_q = """
                                SELECT id, name FROM tags;
                            """
                tags = FlashcardDataBase.normalize_result(cursor.execute(get_tag_ids_q).fetchall())

                clear_tc_relations_q = """
                                DELETE FROM cards_in_tags WHERE card_id = ?;
                            """
                args = (flashcard.id,)

                cursor.execute(clear_tc_relations_q, args)

                for tag in flashcard.tags:
                    tag = tag.encode(encoding="UTF-8", errors="replace")
                    if tag in tags[1]:
                        insert_tc_relation_q = """
                            INSERT INTO cards_in_tags (card_id, tag_id) VALUES (?, ?);
                        """
                        args = (flashcard.id, tags[0][tags[1].index(tag)])
                        cursor.execute(insert_tc_relation_q, args)

                connection.commit()

    @staticmethod
    def clear_database(database: str):
        if not os.path.isfile(database):
            return None

        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()

            delete_q = "DELETE FROM cards;"
            cursor.execute(delete_q)

            delete_q = "DELETE FROM tags;"
            cursor.execute(delete_q)

            delete_q = "DELETE FROM boxes;"
            cursor.execute(delete_q)

            delete_q = "DELETE FROM content_lines;"
            cursor.execute(delete_q)

            delete_q = "DELETE FROM cards_in_tags;"
            cursor.execute(delete_q)

            delete_q = "DELETE FROM cards_in_boxes;"
            cursor.execute(delete_q)

            connection.commit()

    @staticmethod
    def create_database(filename:str):

        # simple way to create the file
        with open(filename, "w") as f:
            pass

        with sqlite3.connect(filename) as connection:
            cursor = connection.cursor()

            cards_q = """
                CREATE TABLE cards (
                    id INT NOT NULL UNIQUE,
                    last_update TIMESTAMP NOT NULL
                );
            """

            boxes_q = """
                CREATE TABLE boxes (
                    id INT NOT NULL UNIQUE,
                    name VARBINARY(150) NOT NULL UNIQUE,
                    color CHAR(6),
                    nr_compartments INT NOT NULL,
                    creation_date TIMESTAMP NOT NULL,
                    last_update TIMESTAMP NOT NULL,
                    special BOOLEAN NOT NULL,
                    cards_left INT NOT NULL
                );
            """

            content_lines_q = """
                CREATE TABLE content_lines (
                    text VARBINARY(1000) NOT NULL,
                    is_def BOOL,
                    card_id INT
                );
            """

            tags_q = """
                CREATE TABLE tags (
                    id INT NOT NULL UNIQUE,
                    name VARBINARY(150) NOT NULL UNIQUE,
                    color CHAR(6),
                    last_update TIMESTAMP NOT NULL
                );
            """

            cards_in_boxes_q = """
                CREATE TABLE cards_in_boxes (
                    card_id INT NOT NULL,
                    box_id INT NOT NULL,
                    comp_nr INT NOT NULL
                );
            """

            cards_in_tags_q = """
                CREATE TABLE cards_in_tags (
                    card_id INT NOT NULL,
                    tag_id INT NOT NULL
                );
            """

            for query in [cards_q, cards_in_boxes_q, cards_in_tags_q, boxes_q, content_lines_q, tags_q]:
                cursor.execute(query)

            connection.commit()
