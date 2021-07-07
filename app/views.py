import json
import os

import pandas as pd
from django.core import serializers
from django.http import HttpResponse, JsonResponse, FileResponse
from sklearn.linear_model import LogisticRegression
from django.forms import model_to_dict
from app.models import userData, users, userPermission
from django_pandas.io import read_frame


def statusCode(code, msg):
    result = {
        'code': code,
        'msg': msg,
    }
    return result


def getPermissionData(request):
    if permission(request.session.get('username')) < 2:
        result = statusCode(400, 'no permission')
        return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="application/json")
    else:
        data = userPermission.objects.all()

        jsonList = []
        for i in data:
            jsonDict = model_to_dict(i)
            jsonDict['username'] = i.userID.username
            jsonList.append(jsonDict)

        result = {
            'code': 0,
            'message': 'success',
            'data': jsonList,
        }
        return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="application/json")


def getTableData(request):
    if permission(request.session.get('username')) == 0:
        result = statusCode(400, 'no permission')
        return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="application/json")
    else:
        rangeA = int(request.POST.get('rangeA'))
        rangeB = int(request.POST.get('rangeB'))
        print(rangeA, rangeB)
        data = userData.objects.all()[rangeA:rangeB]
        data = serializers.serialize("json", data)
        data = json.loads(data)
        result = {
            'code': 0,
            'message': 'success',
            'data': data,
        }
        return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="application/json")


def getAllCount(request):
    data = userData.objects.all().count()
    result = {
        'code': 0,
        'message': 'success',
        'data': data,
    }
    return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="application/json")


def register(request):
    usernameCount = users.objects.filter(username=request.POST.get('username')).count()

    if usernameCount > 0:
        result = statusCode(400, 'User name already exits!')
    else:
        user = users()
        user.username = request.POST.get('username')
        user.password = request.POST.get('password')
        user.phoneNumber = request.POST.get('phoneNumber')
        user.save()
        userPermission.objects.create(
            permission=0,
            userID=user
        )
        result = statusCode(200, 'register success!')
    return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="application/json")


def login(request):
    username = request.POST.get('username')
    password = request.POST.get('password')

    sign = users.objects.filter(username=username).filter(password=password).count()
    if sign == 0:
        result = statusCode(400, '用户名或密码错误！')
    else:
        request.session['username'] = username
        result = statusCode(200, '登陆成功')
    return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="application/json")


def loginCheck(request):
    result = {
        'code': 0,
        'username': '',
    }
    if request.session.get('username'):
        result['code'] = 200
        result['username'] = request.session['username']
    else:
        result['code'] = 400
    return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="application/json")


def predictData():
    current_dir = os.path.dirname(os.path.realpath('__file__'))
    train_filename = os.path.join(current_dir, 'app/data/pfm_train.csv')
    qs = userData.objects.all()
    train_data = pd.read_csv(train_filename)
    test_data = read_frame(qs=qs)
    copy_data = test_data
    train_data.isnull().mean()
    test_data.isnull().mean()
    pd.set_option('expand_frame_repr', False)
    train_data = train_data.drop(['StandardHours', 'Over18', 'EmployeeNumber'], axis=1)
    test_data = test_data.drop(['userID', 'StandardHours', 'Over18', 'EmployeeNumber'], axis=1)
    Attrition = train_data['Attrition']
    train_data.drop(['Attrition'], axis=1, inplace=True)
    train_data.insert(0, 'Attrition', Attrition)
    train_data['MonthlyIncome'] = pd.cut(train_data['MonthlyIncome'], bins=10)
    test_data['MonthlyIncome'] = pd.cut(test_data['MonthlyIncome'], bins=10)
    train_encode = pd.get_dummies(train_data)
    test_encode = pd.get_dummies(test_data)
    train_encode.drop(['TotalWorkingYears', 'YearsWithCurrManager'], axis=1, inplace=True)
    test_encode.drop(['TotalWorkingYears', 'YearsWithCurrManager'], axis=1, inplace=True)
    X_train = train_encode.iloc[:, 1:]
    y_train = train_encode.iloc[:, 0]
    X_test = test_encode.iloc[:, 0:]
    lr = LogisticRegression(max_iter=100000)
    lr.fit(X_train, y_train)
    lr.score(X_train, y_train)
    pred = lr.predict(X_test)
    y_pred = pred
    for i in range(y_pred.size):
        if y_pred[i]:
            copy_data.loc[i, 'Attrition'] = 100
    copy_data = copy_data[copy_data['Attrition'] == 100]
    copy_data.drop(['Attrition'], axis=1)
    return copy_data


def getPredictData(request):
    if permission(request.session.get('username')) == 0:
        result = statusCode(400, 'no permission')
        return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="application/json")
    else:
        predictDataFrame = predictData()
        result = predictDataFrame.to_json(orient='records', force_ascii=False)
        return JsonResponse(json.loads(result), safe=False, json_dumps_params={'ensure_ascii': False})


def downloadPredictCSV(request):
    predictDataFrame = predictData()
    current_dir = os.path.dirname(os.path.realpath('__file__'))
    filename = os.path.join(current_dir, 'app/predictData.csv')
    predictDataFrame.to_csv(filename)
    file = open(filename, 'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="predictData.csv"'
    return response


def logOut(request):
    del request.session['username']
    request.session.flush()
    result = statusCode(200, '退出登录成功')
    return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="application/json")


def postFormData(request):
    data = json.loads(request.body)
    data = data['ruleForm']
    print(data['Age'])
    result = {
        'code': 0,
        'username': request.session.get('username'),
    }
    if request.session.get('username'):
        user = users.objects.values('id').filter(username=request.session.get('username'))
        # count = userData.objects.filter(userID_id=user[0]['id']).count()
        count = userData.objects.filter(userID=user[0]['id']).count()
        print('count=', count, user[0]['id'])
        if count > 0:
            userData.objects.filter(userID=user[0]['id']).update(
                Age=data['Age'],
                BusinessTravel=data['BusinessTravel'],
                Department=data['Department'],
                DistanceFromHome=data['DistanceFromHome'],
                Education=data['Education'],
                EducationField=data['EducationField'],
                EmployeeNumber=data['EmployeeNumber'],
                EnvironmentSatisfaction=data['EnvironmentSatisfaction'],
                Gender=data['Gender'],
                JobInvolvement=data['JobInvolvement'],
                JobLevel=data['JobLevel'],
                JobRole=data['JobRole'],
                JobSatisfaction=data['JobSatisfaction'],
                MaritalStatus=data['MaritalStatus'],
                MonthlyIncome=data['MonthlyIncome'],
                NumCompaniesWorked=data['NumCompaniesWorked'],
                Over18=data['Over18'],
                OverTime=data['OverTime'],
                PercentSalaryHike=data['PercentSalaryHike'],
                PerformanceRating=data['PerformanceRating'],
                RelationshipSatisfaction=data['RelationshipSatisfaction'],
                StandardHours=data['StandardHours'],
                StockOptionLevel=data['StockOptionLevel'],
                TotalWorkingYears=data['TotalWorkingYears'],
                TrainingTimesLastYear=data['TrainingTimesLastYear'],
                WorkLifeBalance=data['WorkLifeBalance'],
                YearsAtCompany=data['YearsAtCompany'],
                YearsInCurrentRole=data['YearsInCurrentRole'],
                YearsSinceLastPromotion=data['YearsSinceLastPromotion'],
                YearsWithCurrManager=data['YearsWithCurrManager'],
            )
        else:
            userData.objects.create(
                Age=data['Age'],
                BusinessTravel=data['BusinessTravel'],
                Department=data['Department'],
                DistanceFromHome=data['DistanceFromHome'],
                Education=data['Education'],
                EducationField=data['EducationField'],
                EmployeeNumber=data['EmployeeNumber'],
                EnvironmentSatisfaction=data['EnvironmentSatisfaction'],
                Gender=data['Gender'],
                JobInvolvement=data['JobInvolvement'],
                JobLevel=data['JobLevel'],
                JobRole=data['JobRole'],
                JobSatisfaction=data['JobSatisfaction'],
                MaritalStatus=data['MaritalStatus'],
                MonthlyIncome=data['MonthlyIncome'],
                NumCompaniesWorked=data['NumCompaniesWorked'],
                Over18=data['Over18'],
                OverTime=data['OverTime'],
                PercentSalaryHike=data['PercentSalaryHike'],
                PerformanceRating=data['PerformanceRating'],
                RelationshipSatisfaction=data['RelationshipSatisfaction'],
                StandardHours=data['StandardHours'],
                StockOptionLevel=data['StockOptionLevel'],
                TotalWorkingYears=data['TotalWorkingYears'],
                TrainingTimesLastYear=data['TrainingTimesLastYear'],
                WorkLifeBalance=data['WorkLifeBalance'],
                YearsAtCompany=data['YearsAtCompany'],
                YearsInCurrentRole=data['YearsInCurrentRole'],
                YearsSinceLastPromotion=data['YearsSinceLastPromotion'],
                YearsWithCurrManager=data['YearsWithCurrManager'],
                userID_id=user[0]['id']
            )

        result['code'] = 200
        result['username'] = request.session['username']
        result = statusCode(200, '提交成功')
    else:
        result['code'] = 400

    return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="application/json")


def getMyInfo(request):
    data = json.loads(request.body)

    userID = users.objects.values('id').filter(username=data['username'])
    userID = userID[0]['id']

    myInfo = userData.objects.filter(userID=userID)
    myInfo = serializers.serialize("json", myInfo)  # 获取到的数据类型为字符串(str)
    myInfo = json.loads(myInfo)  # 将字符串数据转成json类型
    result = {
        'code': 0,
        'data': myInfo,
    }

    return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="application/json")


def permission(username):
    if username == '':
        return 0
    userID = users.objects.get(username=username).id
    return userPermission.objects.get(userID=userID).permission


def getPermission(request):
    result = {
        'code': 0,
        'permission': 0,
    }
    if request.session.get('username'):
        result['permission'] = permission(request.session.get('username'))
    return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="application/json")


def delUserInfo(request):
    data = json.loads(request.body)
    result = {
        'code': 200,
        'msg': '',
    }
    print(data['id'])
    try:
        userInfo = userData.objects.get(id=data['id'])
        userInfo.delete()
        result['code'] = 200
        result['msg'] = 'delete success'
    except IndexError:
        result['code'] = 400
        result['msg'] = 'delete error'
    return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="application/json")


def postPermissionData(request):
    data = json.loads(request.body)
    data = data['ruleForm']
    print(data['userID'])
    result = {
        'code': 0,
        'username': request.session.get('username'),
    }
    if permission(request.session.get('username')) >= 2:
        userPermission.objects.filter(userID=data['userID']).update(
            permission=data['permission'],
        )
        result['code'] = 200
        result['username'] = request.session['username']
        result = statusCode(200, '提交成功')
    else:
        result['code'] = 400

    return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="application/json")

