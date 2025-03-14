from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from story.models import *

from member.models import *  # Importing CustomUser model from manager app


def to_index(request):
    # Redirect to counselor-main page if user is already authenticated
    if request.user.is_authenticated:
        return redirect('to-main')

    return render(request, 'index.html', {})


def to_login(request):
    # Redirect to student-main page if user is already authenticated
    # if request.user.is_authenticated:
    #     return redirect('member-main')

    # Handling form submission
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = CustomUser.objects.get(username=email)
            authenticated_user = authenticate(request, username=email, password=password)
            print("user authenticated")

            # If authentication successful, login user
            if authenticated_user:
                print("user authenticated")
                login(request, authenticated_user)
                print("user logged in")
                return redirect('to-main')
            else:
                messages.error(request, "Invalid login credentials")
                print("Invalid credentials")
                return redirect('to-login')

        except CustomUser.DoesNotExist:
            # Handle non-existing user
            messages.error(request, "User does not exist")
            print("User does not exist")
            return redirect('to-login')

    # Render login page if request method is GET
    return render(request, 'login.html', {})

@login_required
def to_logout(request):
    logout(request)
    return redirect('to-index')
def to_signup(request):
    # Handling form submission
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('passwordconfirm')


        # Check if username already exists
        if CustomUser.objects.filter(username=email).exists():
            messages.error(request, "Username already exists!")
            return redirect('to-signup')

        # Check if all required fields are filled
        if not all([email, password, password_confirm]):
            messages.error(request, "Please fill out all the required fields!")
            return redirect('to-signup')

        # Check if password matches confirm password
        if password == password_confirm:
            # Hash password and create new user
            hashed_password = make_password(password)
            new_user = CustomUser(
                username=email,
                password=hashed_password,
            )
            new_user.save()
            messages.success(request, "User added successfully!")

            return redirect('to-login')

        else:
            messages.error(request, "Password doesn't match. Please try again!")
            return redirect('to-signup')

    return render(request, 'signup.html')


@login_required
def to_write(request):
    import datetime

    curr_user = request.user
    username = curr_user.username

    genre_list = Genre.objects.all()

    genre_name_list = [g.name for g in genre_list]

    isAdmin= curr_user.is_staff

    context = {
        'username': username,
        'isLogin': True,
        'genre_name_list': genre_name_list,
        'isAdmin': isAdmin,

    }

    if request.method == 'POST':
        user = CustomUser.objects.get(username=curr_user.username)
        title = request.POST.get('title')

        selected_genre_name = request.POST.get('selected_genre')
        print(selected_genre_name)
        genre = Genre.objects.filter(name=selected_genre_name)[0]

        maincharacter = request.POST.get('maincharacter')
        timesetting = request.POST.get('timesetting')
        exposition = request.POST.get('exposition')

        today_year = str(datetime.datetime.today().year)
        today_month = str(datetime.datetime.today().month)
        today_day = str(datetime.datetime.today().day)

        started_date = "-".join([today_year, today_month, today_day])

        from keybert import KeyBERT
        kw_model = KeyBERT()
        keywords_mmr = kw_model.extract_keywords(exposition, keyphrase_ngram_range=(1, 1), stop_words='english',
                                                 use_mmr=True,
                                                 top_n=5, diversity=0.3)
        keyword_list = [km[0] for km in keywords_mmr]  # ['a', 'b', 'c', 'd', 'e']

        suggested_keyword = ", ".join(keyword_list)

        from transformers import pipeline

        # 요약 파이프라인 생성
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        # 요약 실행
        summary = summarizer(exposition, max_length=100, min_length=10, do_sample=False)

        exposition_summary = summary[0]['summary_text']

        new_story = Story(
            user=user,
            started_date = started_date,
            title = title,
            genre = genre,
            main_character = maincharacter,
            time_setting = timesetting,
            suggested_keyword = suggested_keyword,
            exposition_summary = exposition_summary,
        )
        new_story.save()

        new_stage = Stage(
            story=new_story,
            user = user,
            submitted_date = started_date,
            part = 1,
            status = 1,
            text = exposition,
        )
        new_stage.save()

        return redirect('to-main')

    return render(request, 'write.html', context)

@login_required
def to_main(request):
    curr_user = request.user
    username = curr_user.username
    isAdmin = curr_user.is_staff

    author_stages = Stage.objects.filter(user=curr_user, status=3)
    if len(author_stages)>=5:
        new_story_available = True
    else:
        new_story_available = False

    all_storys = Story.objects.all().order_by('started_date')

    story_list = []
    story_last_stage_part_list = []
    all_stages = list(Stage.objects.all().order_by('pk'))
    for story in all_storys:
        curr_story_stage_list = []
        for all_stage in all_stages:
            if all_stage.story == story:
                curr_story_stage_list.append(all_stage)
        if len(curr_story_stage_list) == 5:
            continue
        if curr_story_stage_list[-1].status!=3:
            continue
        story_list.append(story)
        story_last_stage_part_list.append(curr_story_stage_list[-1].PART_CHOICES[curr_story_stage_list[-1].part][1])

    story_exposition_list = [story.exposition_summary for story in story_list]
    # print(story_exposition_list)
    story_pk_list = [story.pk for story in story_list]
    story_genre_list = [story.genre for story in story_list]
    story_title_list = [story.title for story in story_list]




    story_tuple_list = [] # (story , exposition, pk, genre, title)
    for i in range(len(story_list)):
        story_tuple_list.append((story_list[i], story_exposition_list[i], story_pk_list[i], story_genre_list[i], story_title_list[i], story_last_stage_part_list[i]))
    print(story_tuple_list)
    context = {
        'username': username,
        'isLogin': True,
        'isAdmin': isAdmin,
        'story_list': story_list,
        'story_exposition_list': story_exposition_list,
        'story_pk_list': story_pk_list,
        'story_genre_list': story_genre_list,
        'story_title_list': story_title_list,
        'story_tuple_list': story_tuple_list,
        'new_story_available': new_story_available,
    }
    return render(request, 'main.html', context)

@login_required
def to_read(request):
    curr_user = request.user
    isAdmin = curr_user.is_staff
    username = curr_user.username

    all_storys = Story.objects.filter(status=2).order_by('started_date')
    print(all_storys)

    story_list = list(all_storys)
    story_author_list = []
    all_stages = list(Stage.objects.all().order_by('pk'))
    for story in story_list:
        curr_story_author_list = []
        for stage in all_stages:
            if stage.story == story:
                curr_story_author_list.append(stage.user.name)
                #curr_story_author_list.append(stage.user.username)
        story_author_list.append(", ".join(curr_story_author_list))
    story_pk_list = [story.pk for story in story_list]
    story_genre_list = [story.genre for story in story_list]
    story_title_list = [story.title for story in story_list]

    story_tuple_list = []
    for i in range(len(story_list)):
        story_tuple_list.append((story_list[i], story_author_list[i], story_pk_list[i], story_genre_list[i], story_title_list[i]))




    '''
    장르의 종류가 [장르1, 장르2, 장르3, 장르4, ...] 가 있다고 할 때,
    각 유저마다 아래와 같은 vector를 만들어 보자.
    [장르1본횟수, 장르2본횟수, 장르3본횟수, 장르4본횟수, ...]
    
    각 글을 다음과 같은 vector로 표현해 보자.
    자신의 장르에 해당하는 번째만 1이고, 나머지는 0인 vector.
    [0, 0, 0, 1, 0, 0, 0, ...]
    
    그 다음, 각 유저의 vector와 모든 글마다의 vector 간 similarity를 측정해서,
    가장 similarity가 높은 순으로 정렬하여 4개만 보여주는 것임!!!!
    '''
    from pathlib import Path
    # Build paths inside the project like this: BASE_DIR / 'subdir'.
    BASE_DIR = Path(__file__).resolve().parent.parent

    import pickle
    import os
    username = curr_user.username
    picklefile_name = os.path.join(BASE_DIR, 'static') + "/pickle/" + str(curr_user.pk) + '.pickle'
    if os.path.isfile(picklefile_name):
        with open(file=picklefile_name, mode='rb') as f:
            user_history_dict = pickle.load(f)

    else:
        user_history_dict = {
            'genre_pk_list': [],
            'genre_cnt_list': []
        }

    all_genres = Genre.objects.all().order_by('pk')
    all_genres_pk_list = [genre.pk for genre in all_genres]
    genre_vector_list = [
        # 아래처럼 되는 게 목표임!!
        # [1, 0, 0]
        # [0, 1, 0]
        # [0, 0, 1]
    ]

    # ['fantasy', 'romance', 'historical']

    for idx, genre in enumerate(all_genres):
        curr_vector = [0]*len(all_genres)
        curr_vector[idx] += 1
        genre_vector_list.append(curr_vector)

    user_vector = [0]*len(all_genres)
    # 이 시점에서 user_vector는 전체 장르 갯수와 완전히 같은 길이를 갖게 됨
    user_genre_pk_list = user_history_dict['genre_pk_list']
    user_genre_cnt_list = user_history_dict['genre_cnt_list']
    for idx, ugp in enumerate(user_genre_pk_list):
        user_vector[all_genres_pk_list.index(ugp)] += user_genre_cnt_list[idx]
    # 이 시점에서 user_vector는 user가 읽었던 횟수를 완전히 갖고 있게 됨

    all_storys = Story.objects.all().order_by('pk')
    all_story_genre_pk_list = [story.genre.pk for story in all_storys]
    all_story_vector_list = [
        # 아래처럼 되는 게 목표임!!
        # [1, 0, 0] 첫번째 스토리가 판타지
        # [1, 0, 0] 두번째 스토리도 판타지
        # [0, 0, 1] 세번째 스토리가 히스토리컬
        # [0, 1, 0] 네번째 스토리가 로맨스
    ]
    for asgp in all_story_genre_pk_list:
        all_story_vector_list.append(genre_vector_list[all_genres_pk_list.index(asgp)])

    from numpy import dot
    from numpy.linalg import norm

    def cosine_similarity(vec1, vec2):
        return dot(vec1, vec2) / (norm(vec1) * norm(vec2))

    all_story_similarity_list = []
    for asv in all_story_vector_list:
        all_story_similarity_list.append(cosine_similarity(user_vector, asv))

    # tuple 이란 걸 표현할 때 ("수현", 18, "NLCS")
    all_story_tuple_list = []
    for i in range(len(all_storys)):
        all_story_tuple_list.append((all_storys[i], all_story_similarity_list[i]))

    sorted_data = sorted(all_story_tuple_list, key=lambda x: x[1], reverse=True)

    recommended_story_list = [sd[0] for sd in sorted_data[:4]]

    print(recommended_story_list)

    recommended_story_tuple_list = []
    #
    recommended_story_author_list = []
    all_stages = list(Stage.objects.all().order_by('pk'))
    for story in recommended_story_list:
        curr_story_author_list = []
        for stage in all_stages:
            if stage.story == story:
                curr_story_author_list.append(stage.user.name)
                # curr_story_author_list.append(stage.user.username)
        recommended_story_author_list.append(", ".join(curr_story_author_list))
    recommended_story_pk_list = [story.pk for story in recommended_story_list]
    recommended_story_genre_list = [story.genre for story in recommended_story_list]
    recommended_story_title_list = [story.title for story in recommended_story_list]
    for i in range(len(recommended_story_list)):
        recommended_story_tuple_list.append((recommended_story_list[i], recommended_story_author_list[i], recommended_story_pk_list[i], recommended_story_genre_list[i], recommended_story_title_list[i]))

    context = {
        'username': username,
        'isLogin': True,
        'isAdmin': isAdmin,
        'story_list': story_list,
        'story_exposition_list': story_author_list,
        'story_pk_list': story_pk_list,
        'story_genre_list': story_genre_list,
        'story_title_list': story_title_list,
        'recommended_story_tuple_list': recommended_story_tuple_list,
        'story_tuple_list': story_tuple_list,
    }

    return render(request, 'read.html', context)

@login_required
def to_detail(request, id):
    curr_story = Story.objects.get(pk=id)

    curr_user = request.user
    isAdmin = curr_user.is_staff

    from pathlib import Path
    # Build paths inside the project like this: BASE_DIR / 'subdir'.
    BASE_DIR = Path(__file__).resolve().parent.parent

    import pickle
    import os
    username = curr_user.username
    picklefile_name = os.path.join(BASE_DIR, 'static') + "/pickle/" + str(curr_user.pk) + '.pickle'
    if os.path.isfile(picklefile_name):
        with open(file=picklefile_name, mode='rb') as f:
            user_history_dict = pickle.load(f)

    else:
        user_history_dict = {
            'genre_pk_list': [],
            'genre_cnt_list': []
        }

    curr_genre_pk = curr_story.genre.pk

    if curr_genre_pk in user_history_dict['genre_pk_list']:
        user_history_dict['genre_cnt_list'][user_history_dict['genre_pk_list'].index(curr_genre_pk)] += 1
    else:
        user_history_dict['genre_pk_list'].append(curr_genre_pk)
        user_history_dict['genre_cnt_list'].append(1)

    print(user_history_dict)



    with open(file=picklefile_name, mode='wb') as f:
        pickle.dump(user_history_dict, f)

    curr_story_stages = Stage.objects.filter(story=curr_story).order_by('part')
    curr_story_author_list = []
    for css in curr_story_stages:
        curr_story_author_list.append(css.user.username)
    curr_story_authors = ", ".join(curr_story_author_list)
    curr_story_text_list = []
    for css in curr_story_stages:
        curr_story_text_list.append(css.text)
    curr_story_texts = "\n\n".join(curr_story_text_list)



    context = {
        'isAdmin': isAdmin,
        'curr_story': curr_story,
        'curr_story_stages': curr_story_stages,
        'curr_story_authors': curr_story_authors,
        'curr_story_texts': curr_story_texts,
    }

    return render(request, 'detail.html', context)

@login_required
def to_collaborate(request, id):
    curr_user = request.user
    isAdmin = curr_user.is_staff
    curr_story = Story.objects.get(pk=id)

    curr_story_stages = Stage.objects.filter(story=curr_story).order_by('part')

    curr_story_exposition = Stage.objects.filter(story=curr_story, part=1)[0]

    exposition_text = curr_story_exposition.text

    # from keybert import KeyBERT
    # kw_model = KeyBERT()
    # keywords_mmr = kw_model.extract_keywords(exposition_text, keyphrase_ngram_range=(1, 1), stop_words='english',
    #                                          use_mmr=True,
    #                                          top_n=5, diversity=0.3)
    # keyword_list = [km[0] for km in keywords_mmr] # ['a', 'b', 'c', 'd', 'e']
    #
    # suggested_keyword = ", ".join(keyword_list)

    context = {
        'isAdmin': isAdmin,
        'curr_story': curr_story,
        'curr_story_stages': curr_story_stages,

        'pk': curr_story.pk,
    }

    if request.method == 'POST':
        curr_user = request.user

        curr_text = request.POST.get('text')

        story = curr_story
        user = curr_user
        import datetime
        today_year = str(datetime.datetime.today().year)
        today_month = str(datetime.datetime.today().month)
        today_day = str(datetime.datetime.today().day)
        submitted_date = "-".join([today_year, today_month, today_day])
        part = len(curr_story_stages)+1
        status = 1
        text = curr_text

        new_stage = Stage(
            story=story,
            user = user,
            submitted_date = submitted_date,
            part = part,
            status = status,
            text = text,
        )
        new_stage.save()

        return redirect('to-main')

    return render(request, 'collaborate.html', context)

@login_required
def to_inprogress(request):
    curr_user = request.user
    isAdmin = curr_user.is_staff
    username = curr_user.username

    if request.method == 'POST':
        curr_user = request.user

        status = request.POST.get('status')
        pk = request.POST.get('pk')
        # print(pk)
        # print(status)

        status_dict = {
            'Pending': 1,
            'Rejected': 2,
            'Accepted': 3,
        }

        curr_stage = Stage.objects.get(pk=pk)
        curr_stage.status = status_dict[status]
        #TODO:My Submissions 추가되고 나면 기각사유와 기각코드 저장하게 변경하기(models에서 필드도 생성해야함)
        curr_stage.save()

        return redirect('to-inprogress')

    pending_stages = list(Stage.objects.filter(status='1').order_by('pk'))
    pending_stage_part_list = [stage.PART_CHOICES[stage.part-1][1] for stage in pending_stages]
    # for story in story_list:
    #     curr_story_author_list = []
    #     for stage in all_stages:
    #         if stage.story == story:
    #             curr_story_author_list.append(stage.user.name)
    #             #curr_story_author_list.append(stage.user.username)
    #     story_author_list.append(", ".join(curr_story_author_list))
    # story_pk_list = [story.pk for story in story_list]
    # story_genre_list = [story.genre for story in story_list]
    # story_title_list = [story.title for story in story_list]
    #
    stage_tuple_list = []
    for i in range(len(pending_stages)):
         stage_tuple_list.append((pending_stages[i], pending_stage_part_list[i]))
    pending_stage_pk_list = [s.pk for s in pending_stages]
    pending_stage_text_list = [s.text for s in pending_stages]

    pending_storys = Story.objects.filter(status=1).order_by('started_date')

    pending_story_list = list(pending_storys)

    ready_to_publish_story_list = []

    accepted_stages = list(Stage.objects.filter(status=3).order_by('pk'))
    for pending_story in pending_story_list:
        curr_story_stages = []
        for stage in accepted_stages:
            if stage.story == pending_story:
                curr_story_stages.append(stage)
        if len(curr_story_stages) == 5:
            ready_to_publish_story_list.append(pending_story)
    # print(ready_to_publish_story_list)

    context = {
        'username': username,
        'isLogin': True,
        'isAdmin': isAdmin,
        'stage_tuple_list': stage_tuple_list,
        'ready_to_publish_story_list': ready_to_publish_story_list,
        'pending_stage_pk_list': pending_stage_pk_list,
        'pending_stage_text_list': pending_stage_text_list,

        # 'story_list': story_list,
        # 'story_exposition_list': story_author_list,
        # 'story_pk_list': story_pk_list,
        # 'story_genre_list': story_genre_list,
        # 'story_title_list': story_title_list,
        # 'story_tuple_list': story_tuple_list,
    }

    return render(request, 'inprogress.html', context)

@login_required
def to_genre_management(request):
    curr_user = request.user
    isAdmin = curr_user.is_staff
    username = curr_user.username

    active_genres = Genre.objects.filter(is_active=True).order_by('pk')

    context = {
        'username': username,
        'isLogin': True,
        'isAdmin': isAdmin,
        'active_genres': active_genres,
    }

    return render(request, 'genre_management.html', context)

@login_required
def to_add_genre(request):
    curr_user = request.user
    isAdmin = curr_user.is_staff
    username = curr_user.username

    if request.method == 'POST':
        curr_user = request.user

        name = request.POST.get('name')
        genre_delete_check = request.POST.get('genre_delete_check')
        print(genre_delete_check)
        # TODO: Genre에 이미지 저장할 필드 생성하고 추가할 수 있게 바꿔야함
        new_genre = Genre(
            name=name,
        )
        new_genre.save()

        return redirect('to-genremanagement')

    context = {
        'username': username,
        'isLogin': True,
        'isAdmin': isAdmin,
    }

    return render(request, 'genre_management.html', context)

@login_required
def to_delete_genre(request):
    curr_user = request.user
    isAdmin = curr_user.is_staff
    username = curr_user.username

    if request.method == 'POST':
        curr_user = request.user

        delete_genre_pk_list_str = request.POST.getlist('genre_delete_check')
        delete_genre_pk_list = [int(pk) for pk in delete_genre_pk_list_str]
        print(delete_genre_pk_list)
        for delete_genre_pk in delete_genre_pk_list:
            delete_genre = Genre.objects.get(pk=delete_genre_pk)
            delete_genre.is_active=False
            delete_genre.save()

        return redirect('to-genremanagement')

    context = {
        'username': username,
        'isLogin': True,
        'isAdmin': isAdmin,
    }

    return render(request, 'genre_management.html', context)















