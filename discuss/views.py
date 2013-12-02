from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
import random

# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required

# Needed to manually create HttpResponses or raise an Http404 exception
from django.http import HttpResponse, Http404

# Used to create and manually log in a user
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate

# Helper function to guess a MIME type from a file name
from mimetypes import guess_type

from models import *

SITUATIONAL_TOPICS = ['book','movie','song','show','person','story']
ANIMALS = ['tiger', 'owl', 'giraffe', 'parrot']
ANIMAL_COLORS = ['#F7D11B', '#88288B', '#34F8F2', '#C4029B', '#11584B', '#BE242C']

def index(request):
    return render(request, 'discuss/index.html')

@login_required
def discuss(request, id):
	errors = []

	discuss = Discussion.objects.get(id = id)
	
	# ensure only correct user can see discussion
	
	if (discuss.userA != request.user and request.user.is_superuser == False ):
		errors.append('User not authenticated for that discussion')
		context = {'errors': errors}
		return render(request, 'discuss/index.html', context)
	
	if request.method == 'POST':
		# in article selection page
		if 'article' in request.POST:
			article = request.POST['article']
			articleA = Article.objects.get(id = article)
			discuss.articleA = articleA
			discuss.save()
			# find the matching discussion and update its articleB
			discussB = Discussion.objects.filter(userA = discuss.userB).filter(userB = discuss.userA)[0]
			discussB.articleB = articleA
			discussB.save()
		elif 'state' in request.POST and request.POST['state'] == 'discuss':
			# user must select an article, complain at them if they don't
			errors.append('You must select an article!')
			articles = Article.objects.all()
			context = {'discussid':discuss.id, 'articles':articles, 'errors': errors}
			return render(request, 'discuss/articleselection.html', context)
		# in discussion page, handle structured interaction state changes 
		if 'currentstate' in request.POST:
			currentState = request.POST['currentstate']
			dState = DiscussionState.objects.get(discuss=discuss)
			profileA = UserProfile.objects.get(user=discuss.userA)
			profileB = UserProfile.objects.get(user=discuss.userB)
			context = {'discussid':discuss.id, 'profileA':profileA, 'profileB':profileB, 'articleA':discuss.articleA, 'articleB':discuss.articleB, 'errors': errors}
			# Position discrete state handling
			if (currentState == 'position'):
				if (dState.state != currentState):
					return errorRender(request, 'State error: position', 'discuss/discussionposition.html', discuss, errors)
				position = Position.objects.filter(discuss=discuss)
				if len(position) < 1:
					position = Position(discuss = discuss, user = discuss.userA)
					position.save()
				else:
					position = position[0]
				if 'answer1' not in request.POST or 'answer2' not in request.POST or 'answer3' not in request.POST or 'answer4' not in request.POST:
					# user must answer all questions, complain at them if they don't
					return errorRender(request, 'Please answer all questions for your partner', 'discuss/discussionposition.html', discuss, errors)
				else:
					position.answer1 = int(request.POST['answer1'])
					position.answer2 = int(request.POST['answer2'])
					position.answer3 = int(request.POST['answer3'])
					position.answer4 = int(request.POST['answer4'])
					position.save()
					# go straight into context state, don't need to sync with partner
					dState.finished = False
					dState.state = 'context'
					dState.save()
			# Context discrete state handling
			elif (currentState == 'context'):
				if (dState.state != currentState):
					return errorRender(request, 'State error: context', 'discuss/discussioncontext.html', discuss, errors)
				contextual = Context.objects.filter(discuss=discuss)
				if len(contextual) < 1:
					contextual = Context(discuss = discuss, user = discuss.userA)
					contextual.save()
				else:
					contextual = contextual[0]
				if 'answer1' not in request.POST or 'answer2' not in request.POST or 'answer3' not in request.POST:
					# user must answer all questions, complain at them if they don't
					return errorRender(request, 'Please answer all questions for your partner', 'discuss/discussioncontext.html', discuss, errors)
				else:
					contextual.answer1 = int(request.POST['answer1'])
					contextual.answer2 = int(request.POST['answer2'])
					contextual.answer3 = int(request.POST['answer3'])
					contextual.save()
					dState.finished = True
					dState.save()
			# Situational fill-in-the-blank state handling
			elif (currentState == 'situational'):
				if (dState.state != currentState):
					return errorSituational(request, 'State error: situational', discuss, errors)	
				situational = Situational.objects.filter(discuss=discuss)
				if len(situational) < 1:
					situational = Situational(discuss = discuss, user = discuss.userA)
					situational.save()
				else:
					situational = situational[0]
				
				if 'answer' not in request.POST or 'option' not in request.POST or request.POST['option'] == '':
					return errorSituational(request, 'Please answer all questions for your partner', discuss, errors)

				option = request.POST['option']
				answers = request.POST.getlist('answer')
				answerIndex = SITUATIONAL_TOPICS.index(option)
				answer = answers[answerIndex]
					
				if 'text' not in request.POST or request.POST['text'] == '' or answer == '':
					# user must answer all questions, complain at them if they don't
					return errorSituational(request, 'Please answer all questions for your partner', discuss, errors)
				else:
					situational.option = option
					situational.answer = answer
					situational.text = request.POST['text']
					situational.save()
					dState.finished = True
					dState.save()
		# Free talk state handling
			elif (currentState == 'free'):
				if (dState.state != currentState):
					return errorFree(request, 'State error: free talk', discuss, errors)
				if 'text' not in request.POST or request.POST['text'] == '':
					return errorFree(request, 'Please fill in the comment box', discuss, errors)
				free = FreeComment(discuss = discuss, user = discuss.userA, text = request.POST['text'])
				free.save()
				dState.finished = True
				dState.save()
		if 'state' in request.POST:
			state = request.POST['state']
			discuss.state = state
			discuss.save()
			
	# fall-through, GET does this as well as finished POST
	state = discuss.state
	if (state == 'start'):
		profileB = UserProfile.objects.get(user=discuss.userB)
		discussB = Discussion.objects.filter(userA=discuss.userB).filter(userB=discuss.userA)[0]
		# generate random animal avatar for user, make sure it's different than partner
		if (discuss.animal == '' or discuss.animalColor == ''):
			generateAnimal(discuss, discussB)
		# conversely, if partner doesn't have animal, generate one for them
		if (discussB.animal == '' or discussB.animalColor == ''):
			generateAnimal(discussB, discuss)
		
		context = {'discussid':discuss.id, 'profile':profileB, 'errors': errors, 'discussB': discussB}
		return render(request, 'discuss/startdiscuss.html', context)
	elif (state == 'articles'):
		articles = Article.objects.all()
		context = {'discussid':discuss.id, 'articles':articles, 'errors': errors}
		return render(request, 'discuss/articleselection.html', context)
	elif (state == 'discuss'):
		profileA = UserProfile.objects.get(user=discuss.userA)
		profileB = UserProfile.objects.get(user=discuss.userB)
		discussB = Discussion.objects.filter(userA=discuss.userB).filter(userB=discuss.userA)[0]
		context = {'discuss':discuss, 'discussB':discussB, 'profileA':profileA, 'profileB':profileB, 'articleA':discuss.articleA, 'articleB':discuss.articleB, 'errors': errors}
		
		dState = DiscussionState.objects.filter(discuss=discuss)
		if len(dState) < 1:
			dState = DiscussionState(discuss = discuss)
			dState.save()
		else:
			dState = dState[0]
		
		context['finished'] = dState.finished
		
		if dState.state == 'articles':
			if discuss.articleA and discuss.articleB:
				dState.state = 'position'
				dState.finished = False
				context['finished'] = dState.finished
				dState.save()
				
			return render(request, 'discuss/discussionarticles.html', context)
		elif dState.state == 'position':
			return render(request, 'discuss/discussionposition.html', context)
		elif dState.state == 'context':
			
			# sync check between partners
			# finished answering questions, now must sync with partner
			if (dState.finished == True):
				discussB = Discussion.objects.filter(userA = discuss.userB).filter(userB = discuss.userA)[0]
				discussStateB = DiscussionState.objects.get(discuss = discussB)
				if ((discussStateB.state == 'context' and discussStateB.finished == True) or discussStateB.state == 'situational'):
						dState.finished = False
						dState.state = 'situational'
						dState.save()
						context['finished'] = dState.finished
						context['situationaltopics'] = SITUATIONAL_TOPICS
						return render(request, 'discuss/discussionsituational.html', context)

			return render(request, 'discuss/discussioncontext.html', context)
		elif dState.state == 'situational':
		
			discussB = Discussion.objects.filter(userA = discuss.userB).filter(userB = discuss.userA)[0]
			addDiscreteToContext(discuss, discussB, context)
			
			# sync check between partners
			# finished answering questions, now must sync with partner
			if (dState.finished == True):
				discussB = Discussion.objects.filter(userA = discuss.userB).filter(userB = discuss.userA)[0]
				discussStateB = DiscussionState.objects.get(discuss = discussB)
				if ((discussStateB.state == 'situational' and discussStateB.finished == True) or discussStateB.state == 'free'):
						dState.finished = False
						dState.state = 'free'
						dState.save()
						context['finished'] = dState.finished
						return render(request, 'discuss/discussionfree.html', context)
						
			context['situationaltopics'] = SITUATIONAL_TOPICS
			return render(request, 'discuss/discussionsituational.html', context)
			
		elif dState.state == 'free':
			discussB = Discussion.objects.filter(userA = discuss.userB).filter(userB = discuss.userA)[0]
			addDiscreteToContext(discuss, discussB, context)
			
			sitA = Situational.objects.get(discuss=discuss)
			sitB = Situational.objects.get(discuss=discussB)
			
			context['sitA'] = sitA
			context['sitB'] = sitB
			context['comments'] = getComments(discuss)
			context['finished'] = dState.finished
			return render(request, 'discuss/discussionfree.html', context)
				
		return render(request, 'discuss/discussionbase.html', context)
	return render(request, 'discuss/startdiscuss.html')
	
# convienence method for re-rendering discuss page with errormsg
def errorRender(request, errormsg, templateurl, discuss, errors):
	errors.append(errormsg)
	profileA = UserProfile.objects.get(user=discuss.userA)
	profileB = UserProfile.objects.get(user=discuss.userB)
	discussB = Discussion.objects.filter(userA=discuss.userB).filter(userB=discuss.userA)[0]
	context = {'discuss':discuss, 'discussB':discussB, 'profileA':profileA, 'profileB':profileB, 'articleA':discuss.articleA, 'articleB':discuss.articleB, 'errors': errors}
	return render(request, templateurl, context)

# special version of errorRender that includes situational association topics
def errorSituational(request, errormsg, discuss, errors):
	errors.append(errormsg)
	profileA = UserProfile.objects.get(user=discuss.userA)
	profileB = UserProfile.objects.get(user=discuss.userB)
	discussB = Discussion.objects.filter(userA=discuss.userB).filter(userB=discuss.userA)[0]

	context = {'discuss':discuss, 'discussB':discussB, 'profileA':profileA, 'profileB':profileB, 'articleA':discuss.articleA, 'articleB':discuss.articleB, 'errors': errors, 'situationaltopics':SITUATIONAL_TOPICS}
	
	addDiscreteToContext(discuss, discussB, context)
	
	return render(request, 'discuss/discussionsituational.html', context)
	
# special version of errorRender that includes existing topics
def errorFree(request, errormsg, discuss, errors):
	errors.append(errormsg)
	profileA = UserProfile.objects.get(user=discuss.userA)
	profileB = UserProfile.objects.get(user=discuss.userB)
	discussB = Discussion.objects.filter(userA = discuss.userB).filter(userB = discuss.userA)[0]

	context = {'discuss':discuss, 'discussB':discussB, 'profileA':profileA, 'profileB':profileB, 'articleA':discuss.articleA, 'articleB':discuss.articleB, 'errors': errors, 'comments':getComments(discuss)}
	
	addDiscreteToContext(discuss, discussB, context)
	return render(request, 'discuss/discussionfree.html', context)

# aggregates free text comments from both discussion instances (users)
def getComments(discuss):
	allComments = []
	comments = FreeComment.objects.filter(discuss=discuss)
	discussB = Discussion.objects.filter(userA = discuss.userB).filter(userB = discuss.userA)[0]
	commentsB = FreeComment.objects.filter(discuss=discussB)
	for comment in comments:
		allComments.append(comment)
	for comment in commentsB:
		allComments.append(comment)
	comments = sorted(allComments, key=lambda comment: comment.time, reverse=True)
	return comments

# randomly creates avatar animal and color for discussA, makes sure it's different than discussB
def generateAnimal(discussA, discussB):
	animalB = discussB.animal
	animalColorB = discussB.animalColor
	animalList = list(ANIMALS)
	animalColorList = list(ANIMAL_COLORS)
	if (animalList.count(animalB) > 0):
		animalList.remove(animalB)
	if (animalColorList.count(animalColorB) > 0):
		animalColorList.remove(animalColorB)
	animal = animalList[random.randint(0, len(animalList) - 1)]
	animalColor = animalColorList[random.randint(0, len(animalColorList) - 1)]
	discussA.animal = animal
	discussA.animalColor = animalColor
	discussA.save()

# adds converted discrete answers into context
def addDiscreteToContext(discussA, discussB, context):
	contextA = Context.objects.get(discuss=discussA)
	positionA = Position.objects.get(discuss=discussA)
	
	positionB = Position.objects.get(discuss=discussB)
	contextB = Context.objects.get(discuss=discussB)
	
	posAans = [positionA.answer1, positionA.answer2, positionA.answer3, positionA.answer4]
	posAans = convertPosition(posAans)
	posBans = [positionB.answer1, positionB.answer2, positionB.answer3, positionB.answer4]
	posBans = convertPosition(posBans)
	
	conAans = [contextA.answer1, contextA.answer2, contextA.answer3]
	conAans = convertContext(conAans)
	conBans = [contextB.answer1, contextB.answer2, contextB.answer3]
	conBans = convertContext(conBans)
	
	context['positionA'] = posAans
	context['positionB'] = posBans
	context['contextA'] = conAans
	context['contextB'] = conBans
	
	return context
	
# converts position answer ints into words
def convertPosition(answers):
	answer1texts = ['really bad', 'bad', 'somewhat bad', 'neutral', 'somewhat good', 'good', 'really good']
	answer2texts = ['completely unsurprising', 'unsurprising', 'somewhat unsurprising', 'neither surprising nor unsurprising', 'somewhat surprising', 'surprising', 'really surprising']
	answer3texts = ['strongly disagree', 'disagree', 'somewhat disagree', 'neither disagree nor agree', 'somewhat agree', 'agree', 'strongly agree']
	answer4texts = ['completely different', 'different', 'somewhat different', 'neutral', 'somewhat similar', 'similar', 'the same']
	return [answer1texts[answers[0]-1], answer2texts[answers[1]-1], answer3texts[answers[2]-1], answer4texts[answers[3]-1]]

# converts context answer ints into words
def convertContext(answers):
	answer1texts = ['never', 'rarely', 'not often', 'neutral', 'sometimes', 'often', 'all the time']
	answer2texts = ['always the same', 'mostly the same', 'sometimes the same', 'neutral', 'changed at some point', 'changed', 'changed recently']
	answer3texts = ['completely differently than me', 'differently than me', 'somewhat differently than me', 'neither different nor the same', 'somewhat similarly', 'similarly', 'all about the same as I do']
	return [answer1texts[answers[0]-1], answer2texts[answers[1]-1], answer3texts[answers[2]-1]]

@login_required
def get_photo(request, id):
    entry = get_object_or_404(UserProfile, id=id)
    if not entry.avatar:
        raise Http404

    content_type = guess_type(entry.avatar.name)
    return HttpResponse(entry.avatar, mimetype=content_type)

# ajax function for free comment page	
@login_required
def comments(request, id):
	errors = []
	discuss = Discussion.objects.get(id = id)
	# meant to be called by periodic ajax function
	if request.method == 'GET':
		context = {'comments':getComments(discuss), 'userA':discuss.userA, 'userB':discuss.userB}
		return render(request, 'discuss/comments.xml', context, content_type='application/xml')
	# meant to be called by submit button
	elif request.method == 'POST':
		currentState = request.POST['currentstate']
		dState = DiscussionState.objects.get(discuss=discuss)
		if (dState.state != currentState):
			return errorFree(request, 'State error: free talk', discuss, errors)
		if 'text' not in request.POST or request.POST['text'] == '':
			return errorFree(request, 'Please fill in the comment box', discuss, errors)
		free = FreeComment(discuss = discuss, user = discuss.userA, text = request.POST['text'])
		free.save()
		dState.finished = True
		dState.save()
		context = {'comments':getComments(discuss), 'userA':discuss.userA, 'userB':discuss.userB}
		return render(request, 'discuss/comments.xml', context, content_type='application/xml')
		
@login_required
def articlecheck(request, id):
	errors = []
	discuss = Discussion.objects.get(id = id)
	dState = DiscussionState.objects.get(discuss=discuss)
	if dState.state != 'articles' and dState.state != 'position':
		return errorRender(request, 'State error: articles', 'discuss/discussionarticles.html', discuss, errors)
	if discuss.articleA and discuss.articleB:
		dState.state = 'position'
		dState.finished = False
		dState.save()
		context = {'done':1}
		return render(request, 'discuss/check.xml', context, content_type='application/xml')
	context = {'done':0}
	return render(request, 'discuss/check.xml', context, content_type='application/xml')
	
@login_required
def contextcheck(request, id):
	errors = []
	discuss = Discussion.objects.get(id = id)
	dState = DiscussionState.objects.get(discuss=discuss)
	if dState.state != 'context' and dState.state != 'situational':
		return errorRender(request, 'State error: context', 'discuss/discussioncontext.html', discuss, errors)

	if (dState.finished == True):
		discussB = Discussion.objects.filter(userA = discuss.userB).filter(userB = discuss.userA)[0]
		discussStateB = DiscussionState.objects.get(discuss = discussB)
		if ((discussStateB.state == 'context' and discussStateB.finished == True) or discussStateB.state == 'situational'):
			dState.finished = False
			dState.state = 'situational'
			dState.save()
			context = {'done':1}
			return render(request, 'discuss/check.xml', context, content_type='application/xml')

	context = {'done':0}
	return render(request, 'discuss/check.xml', context, content_type='application/xml')
	
@login_required
def situationalcheck(request, id):
	errors = []
	discuss = Discussion.objects.get(id = id)
	dState = DiscussionState.objects.get(discuss=discuss)
	if dState.state != 'situational' and dState.state != 'free':
		return errorSituational(request, 'State error: situational', discuss, errors)
	
	if (dState.finished == True):
		discussB = Discussion.objects.filter(userA = discuss.userB).filter(userB = discuss.userA)[0]
		discussStateB = DiscussionState.objects.get(discuss = discussB)
		
		if ((discussStateB.state == 'situational' and discussStateB.finished == True) or discussStateB.state == 'free'):
			dState.finished = False
			dState.state = 'free'
			dState.save()
			context = {'done':1}
			return render(request, 'discuss/check.xml', context, content_type='application/xml')

	context = {'done':0}
	return render(request, 'discuss/check.xml', context, content_type='application/xml')