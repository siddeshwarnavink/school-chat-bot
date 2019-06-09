# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import requests
import json
import mysql.connector #pylint: disable=import-error
from rasa_core_sdk import Action  #pylint: disable=import-error

logger = logging.getLogger(__name__)

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="password123",
  database="abcschool"
)

class ActionJoke(Action):
    def name(self):
        # define the name of the action which can then be included in training stories
        return "action_joke"

    def run(self, dispatcher, tracker, domain):
        # what your action should do
        request = json.loads(
            requests.get("https://api.chucknorris.io/jokes/random").text
        )  # make an api call
        joke = request["value"]  # extract a joke from returned json response
        dispatcher.utter_message(joke)  # send the message back to the user
        return []

class ActionClass(Action):
    def name(self):
        return "action_class"

    def run(self, dispatcher, tracker, domain):
        mycursor = mydb.cursor()

        classLabel = tracker.get_slot('classIdent')

        mycursor.execute("SELECT c.id, c.label, c.strength, t.name as class_teacher FROM classes c, teachers t WHERE t.id = c.class_teacher AND c.label LIKE '{}';".format(classLabel))
        classResults = mycursor.fetchone()

        classData = {
            "label":  classResults[1],
            "strength": classResults[2],
            "class_teacher":  classResults[3]
        }

        dispatcher.utter_message("{} is a class handled by {} contains {} student(s)".format(classData['label'], classData['class_teacher'], classData['strength']))
        return []


class ActionClassStudentTopper(Action):
    def name(self):
        return "action_class_student_topper"

    def run(self, dispatcher, tracker, domain):
        mycursor = mydb.cursor()

        classLabel = tracker.get_slot('classIdent')

        mycursor.execute("SELECT id FROM classes WHERE label LIKE '{}';".format(classLabel))
        classId = mycursor.fetchone()[0]

        mycursor.execute('SELECT id, name, overall_rank FROM abcschool.students WHERE class = {} AND overall_rank = "A+" OR overall_rank = "A";'.format(classId))
        classTopper = mycursor.fetchone()

        classTopperData = {
            "name": classTopper[1],
            "overall_rank": classTopper[2]
        }

        dispatcher.utter_message("{} is the class topper with {} grade".format(classTopperData['name'], classTopperData['overall_rank']))
        return []

class ActionClassTeachers(Action):
    def name(self):
        return "action_class_teachers"

    def run(self, dispatcher, tracker, domain):
        mycursor = mydb.cursor()

        classLabel = tracker.get_slot('classIdent')

        mycursor.execute('select t.name from classes c, teacher_handling th, teachers t where c.id = th.class and th.teacher = t.id and c.label like "{}";'.format(classLabel))
        classHandlingTeachers = mycursor.fetchall()

        teachers = []
        for teacher in classHandlingTeachers:
            teachers = teachers + "{}, ".format(teacher[0])
        
        teachers = teachers[:-2]

        dispatcher.utter_message("Teacher handling: {}".format(teachers))
        return []