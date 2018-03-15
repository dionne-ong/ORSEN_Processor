from ..SqlConnector import SqlConnConcepts
from src.objects.concepts.Concept import Concept

IS_A = "IsA"
PART_OF = "PartOf"
AT_LOCATION = "AtLocation"
HAS_PREREQ = "HasPrerequisite"
CREATED_BY = "CreatedBy"
USED_FOR = "UsedFor"
CAUSES = "Causes"
DESIRES = "Desires"
CAPABLE_OF = "CapableOf"
HAS_PROPERTY = "HasProperty"


def get_specific_concept(id):
    sql = "SELECT idconcepts, " \
          "relation," \
          "first," \
          "second " \
          "FROM concepts " \
          "WHERE idconcepts = %d;" % id

    conn = SqlConnConcepts.getConnection()
    cursor = conn.cursor()

    resulting = None

    try:
        # Execute the SQL command
        cursor.execute(sql)
        # Fetch all the rows in a list of lists.
        result = cursor.fetchone()
        row = result
        id          = row[0]
        relation    = row[1]
        first       = row[2]
        second      = row[3]

        resulting = Concept(id, relation, first, second)

    except:
        print("Error Concepts: unable to fetch data of character #%d" % id)

    conn.close()
    return resulting


def get_all_concepts():
    sql = "SELECT idconcepts, " \
          "relation," \
          "first," \
          "second " \
          "FROM concepts "

    conn = SqlConnConcepts.getConnection()
    cursor = conn.cursor()

    resulting = []

    try:
        cursor.execute(sql)
        result = cursor.fetchall()

        for row in result:
            id          = row[0]
            relation    = row[1]
            first       = row[2]
            second      = row[3]

            resulting.append(Concept(id, relation, first, second))

    except:
        print("Error Concepts: unable to fetch all data")

    conn.close()
    return resulting


def get_word_concept(word):
    sql = "SELECT idconcepts, " \
          "relation," \
          "first," \
          "second " \
          "FROM concepts " \
          "WHERE first = %s OR second = %s "
    print(sql)
    conn = SqlConnConcepts.getConnection()
    cursor = conn.cursor()

    resulting = []

    try:
        cursor.execute(sql, (word, word,))
        # Fetch all the rows in a list of lists.
        result = cursor.fetchall()

        id = -1
        relation = ""
        first = ""
        second = ""

        for row in result:
            id          = row[0]
            relation    = row[1]
            first       = row[2]
            second      = row[3]

        resulting.append(Concept(id, relation, first, second))

    except:
        print("Error Concept: unable to fetch data for word "+word)

    conn.close()
    return resulting


def get_concept(word, relation):
    sql = "SELECT idconcepts, " \
          "relation," \
          "first," \
          "second " \
          "FROM concepts " \
          "WHERE (first = %s OR second = %s) AND relation = %s "
    print(sql)
    conn = SqlConnConcepts.getConnection()
    cursor = conn.cursor()

    resulting = []

    try:
        # Execute the SQL command
        cursor.execute(sql, (word, word, relation,))
        # Fetch all the rows in a list of lists.
        result = cursor.fetchall()

        for row in result:
            id          = row[0]
            relation    = row[1]
            first       = row[2]
            second      = row[3]

            resulting.append(Concept(id, relation, first, second))

    except:
        print("Error Concept: unable to fetch data for word "+word)

    conn.close()
    return resulting


def add_concept(concept):
    sql = "INSERT INTO concepts " \
          "(relation, " \
          "first, " \
          "second) " \
          "VALUES " \
          "(%s, " \
          " %s, " \
          " %s);"
    print(sql)
    conn = SqlConnConcepts.getConnection()
    cursor = conn.cursor()

    try:
        cursor.execute(sql, (concept.relation, concept.first, concept.second,))
        conn.commit()
        conn.close()
        return True

    except:
        print("Error Concept: unable to insert data "+concept.__str__())
        conn.close()
        return False
