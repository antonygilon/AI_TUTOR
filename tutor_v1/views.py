from django.shortcuts import render
from django.contrib.auth.models import User
import pandas as pd
from django import forms
from django.http import HttpResponse
from django.shortcuts import render
from .forms import UploadQuestions
from .models import Skill,AnswerText,AnswerChoice,Problem, Probability, Student, DiagnosticResult
import string
import subprocess
import os
import numpy as np

# Create your views here.

def insert_questions(questions_file, mapping_file):
	qf = pd.read_csv(questions_file)
	mf = pd.read_csv(mapping_file)
	existing_skills = Skill.objects.all()
	if not existing_skills:
		for id,row in mf.iterrows():
			new_skill = Skill(skill_name = row['skill'],skill_desc = row['skill_description'])
			new_skill.save()
	else:
		existing_skills_list = [skill.skill_name for skill in existing_skills]
		for id,row in mf.iterrows():
			if row['skill'] not in existing_skills_list:
				new_skill = Skill(skill_name = row['skill'],skill_desc = row['skill_description'])
				new_skill.save()

	if 'problem_name' not in qf.columns:
		qf['problem_name'] = ''
	qf.dropna(subset=qf.columns,inplace=True)
	for id,row in qf.iterrows():
		question = None
		choice_begins = list(string.ascii_lowercase)
		list1 = []
		list2 = []
		for char in choice_begins:
			list1.append(char+')')
			list2.append(char+'.')
		choice_begins = list1+list2
		print(row['skill'])
		skill = Skill.objects.get(skill_name = row['skill'])
		answer_type = row['answer_type']
		if answer_type == 'Choice':
			choices = row['answers_list']
			choices = choices.split('\n')
			cleansed_choices = []
			for choice in choices:
				if choice != '':
					if choice[0:2] in choice_begins:
						choice = choice[2:]
					cleansed_choices.append(choice)

			correct_choices = row['correct_answer']
			correct_choices  = correct_choices.split('\n')
			new_correct_choices = []
			for choice in correct_choices:
				new_correct_choices.append(ord(choice))
			new_choice = AnswerChoice(choices = cleansed_choices,correct_choices =new_correct_choices)
			new_choice.save()
			question  = Problem(answer_object = new_choice,problem_name = row['problem_name'],problem_text =row['questions'],skill_id = skill,diagnostic_test = row['diagnostic'])

		elif answer_type == 'Text' or answer_type == 'text':
			answer = row['answers_list']
			answer = answer.strip()
			answer = answer.tolower()
			answer_obj = AnswerText(correct_answer = answer)
			answer_obj.save()
			question = Problem(answer_object = answer, problem_name = row['problem_name'],problem_text = row['questions'], skill_id = skill,diagnostic_test = row['diagnostic'])

		question.save()


def upload_questions(request):
	form = None
	if request.method == 'POST':
		form = UploadQuestions(request.POST, request.FILES)

		if form.is_valid():
			insert_questions(request.FILES['question_file'],request.FILES['mapping_file'])
			return HttpResponse("File Uploaded Successfully")

		else:
			form = UploadQuestions()
	return render(request, 'upload_questions.html', {'form': form})


def compute_knowledge_graph(data_dict,update = False):

	current_user = Student.objects.get(pk = 1)
	correct_or_wrong = 2
	score = 0
	if update:
		file = open("tutor_v1/datasets/hmmdata.txt","a+")
	else:
		file = open("tutor_v1/datasets/hmmdata.txt","w+")
	for key,value in data_dict.items():
		hmm_data = []
		question = Problem.objects.get(pk = key)
		if question.answer_type.name == 'answer choice':
			correct_answer = question.answer_object.correct_choices
			if value == correct_answer:
				correct_or_wrong = 1
				score = score + 1

		elif question.answer_type.name == 'answer text':
			correct_answer = question.answer_object.correct_answer
			if correct_answer == value:
				correct_or_wrong = 1
				score = score+1

		hmm_data.append(str(correct_or_wrong))
		hmm_data.append(current_user.user.username)
		hmm_data.append(str(question.id))
		hmm_data.append(question.skill_id.skill_name.replace(' ','-'))
		hmm_data.append('\n')
		data_string = '\t'.join(hmm_data)
		file.write(data_string)

	result = DiagnosticResult(student_id = current_user, score = score)
	result.save()
	file.close()
	os.system("hmm-scalable/./trainhmm tutor_v1/datasets/hmmdata.txt tutor_v1/datasets/knowledgegraph.txt")
	file = open("tutor_v1/datasets/knowledgegraph.txt","r")
	data_array = file.readlines()
	data_array = data_array[7:]
	final_data_array = []
	probability_dict = {}
	if '' in data_array:
		data_array.remove('')
	for i in range(0,len(data_array),4):
		final_data_array.append(data_array[i:i+4])
	for item in final_data_array:
		skill = str(item[0].split('\t')[1])
		prior_probability = float(item[1].split('\t')[1])
		transition_probability = float(item[2].split('\t')[3])
		slip = float(item[3].split('\t')[2])
		guess = float(item[3].split('\t')[3])
		probability_dict[skill] = {'prior_probability':prior_probability,'transition_probability':transition_probability,
		 'slip':slip,'guess':guess}

	if Probability.objects.all() is not None:
		Probability.objects.all().delete()
	for key,value in probability_dict.items():
		print(key)
		skill_obj = Skill.objects.get(skill_name = key.strip())
		if probability_dict[key]['transition_probability'] > 0.95:
			probability_dict[key]['completed'] = 1
		else:
			probability_dict[key]['completed'] = 0
		prob_obj = Probability(skill_id = skill_obj, student_id = current_user,prior_probability = probability_dict[key]['prior_probability'],
			transition_probability = probability_dict[key]['transition_probability'], slip_probability = probability_dict[key]['slip'],
			guess_probability = probability_dict[key]['guess'],completed = probability_dict[key]['completed'])
		prob_obj.save()



def create_diagnostic_test(request):

	if request.method == 'POST':
		data_dict = dict(request.POST)
		print(data_dict)
		if 'csrfmiddlewaretoken' in data_dict:
			del data_dict['csrfmiddlewaretoken']

		compute_knowledge_graph(data_dict)
		return HttpResponse("Knowledge graph updated Successfully")

	else:
		diagnostic_test = Problem.objects.filter(diagnostic_test=1)
		return render(request,'diagnostic_test.html',{'Questions': diagnostic_test})




def update_hmm(request):

	if request.method == 'POST':
		data_dict = dict(request.POST)
		print(data_dict)
		if 'csrfmiddlewaretoken' in data_dict:
			del data_dict['csrfmiddlewaretoken']

		for key,value in data_dict.items():
			question_id = key
		
		compute_knowledge_graph(data_dict,update=True)
		prob_obj = Probability.objects.filter(completed = 0)
		current_skill = Problem.objects.get(id = question_id).skill_id
		questions = Problem.objects.filter(skill_id = current_skill.id)
		test_file = open('tutor_v1/datasets/hmmtest.txt','w+')
		current_user = Student.objects.get(pk = 1)
		for question in questions:
			write_array = []
			write_array.append('.')
			write_array.append(current_user.user.username)
			write_array.append(str(question.id))
			write_array.append(question.skill_id.skill_name)
			data_string = '\t'.join(write_array)
			test_file.write(data_string)
			test_file.write('\n')
		test_file.close()
		os.system("hmm-scalable/./predicthmm -p 1 tutor_v1/datasets/hmmtest.txt tutor_v1/datasets/knowledgegraph.txt tutor_v1/datasets/predictions.txt")
		pred_file = open("tutor_v1/datasets/predictions.txt","r")
		abs_diff = []
		for line in pred_file.readlines():
			diff = line.split('\t')
			abs_diff.append(float(diff[0]) - float(diff[1]))

		min_index = np.argmax(np.array(abs_diff))
		pred_file.close()
		test_file = open('tutor_v1/datasets/hmmtest.txt')
		test_array = test_file.readlines()
		next_question = test_array[min_index].split('\t')[2]
		return HttpResponse(next_question)



















