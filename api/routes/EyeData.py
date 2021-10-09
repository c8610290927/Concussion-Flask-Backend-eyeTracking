from flask.helpers import get_flashed_messages
from api.models.EyeData import EyeTrackingDataSchema, EyeTrackingData
from api.models.EyeFeatureData import EyeTrackingFeature, EyeTrackingFeatureSchema
from api.models.PlayHistory import PlayHistorySchema, PlayHistory
from api.utils.responses import response_with
from api.utils import responses as resp
from flask import Blueprint, request, send_from_directory, Response
from sqlalchemy.sql import text
import matplotlib.pyplot as plt
import numpy as np
import pickle
import math
import gzip
import json

eyeTracking_routes = Blueprint("eyeTracking_routes", __name__)

# get the picture of eye-tracking
@eyeTracking_routes.route("/get/img/<sessionid>", methods=['GET'])
def GetImage(sessionid):
    """
    GetImage, According sessionid, return a result EyeTracking image
    :param sessionid:
    :return:
    """

    return send_from_directory('static', f'{sessionid}'+'.jpg')

# @eyeTracking_routes.route("/get/session/<username>", methods=['GET'])
# def GetSessionidByUsername(username):
#     """
#     GetSessionidByUsername, According to username, return a list of sessionid by username
#     :param username:
#     :return:
#     """
#     query = PlayHistory.query.filter_by(username=username)
#     sessionid_list = []
#     for i in query:
#         sessionid_list.append(i.sessionid)
#     return Response(json.dumps(sessionid_list),  mimetype='application/json')

#get the result that the chance of getting concussion (saccade)
@eyeTracking_routes.route("/get/saccade_result/<sessionid>")
def GetSaccadeResultBySessionid(sessionid):
    query = EyeTrackingFeature.query.filter_by(sessionid=sessionid).first()
    SVM_model = pickle.load(open('model/SVM_model', 'rb'))
    data = np.array([[query.tracking_dist, query.game_time, query.tracking_speed, query.wink_left, query.wink_right]])
    result = SVM_model.predict(data)
    result_proba = SVM_model.predict_proba(data)
    print("result & result_proba: ",result, result_proba)
    
    return Response(json.dumps(result_proba[0][1]),  mimetype='application/json')

##get the result that the chance of getting concussion (fixation)
@eyeTracking_routes.route("/get/fixation_result/<sessionid>")
def GetFixationResultBySessionid(sessionid):
    query = EyeTrackingFeature.query.filter_by(sessionid=sessionid).first()
    SVM_model = pickle.load(open('model/SVM_model_fixation', 'rb'))
    data = np.array([[query.tracking_dist, query.game_time, query.tracking_speed, query.wink_left, query.wink_right]])
    result = SVM_model.predict(data)
    result_proba = SVM_model.predict_proba(data)
    print("result & result_proba: ",result, result_proba)

    return Response(json.dumps(result_proba[0][1]),  mimetype='application/json')

@eyeTracking_routes.route("/get/dist/<sessionid>")
def GetDistanceBySessionid(sessionid):
    query = EyeTrackingFeature.query.filter_by(sessionid=sessionid).first()
    print(query.tracking_dist)
    return Response(json.dumps(query.tracking_dist),  mimetype='application/json')

@eyeTracking_routes.route("/get/time/<sessionid>")
def GetTimeBySessionid(sessionid):
    query = EyeTrackingFeature.query.filter_by(sessionid=sessionid).first()
    print(query.game_time)
    return Response(json.dumps(query.game_time),  mimetype='application/json')

@eyeTracking_routes.route("/get/speed/<sessionid>")
def GetSpeedBySessionid(sessionid):
    query = EyeTrackingFeature.query.filter_by(sessionid=sessionid).first()
    print(query.tracking_speed)
    return Response(json.dumps(query.tracking_speed),  mimetype='application/json')

@eyeTracking_routes.route("/get/wink_left/<sessionid>")
def GetWinkLBySessionid(sessionid):
    query = EyeTrackingFeature.query.filter_by(sessionid=sessionid).first()
    print(query.wink_left)
    return Response(json.dumps(query.wink_left),  mimetype='application/json')

@eyeTracking_routes.route("/get/wink_right/<sessionid>")
def GetWinkRBySessionid(sessionid):
    query = EyeTrackingFeature.query.filter_by(sessionid=sessionid).first()
    print(query.wink_right)
    return Response(json.dumps(query.wink_right),  mimetype='application/json')

@eyeTracking_routes.route('/receive', methods=['GET', 'POST'])
def Receive():
    file = request.data
    aa = gzip.decompress(file).decode() 
    tt = aa.split('\n')
    mode = ""
    for i in tt:
        row_data = json.loads(i)
        print("receive結果: ", row_data)
        data = {}
        # try:
        # if row_data['Name'] == "DataSync.Entity.ApplicationStartEntity":
        #     print("==================ApplicationStartEntity")
        # Create Play History
        if row_data['Name'] == 'DataSync.Entity.ScopeStartEntity':
            print("==================建立PlayHistory中")
            data['username'] = row_data['Tags']['_userId']
            data['sessionid'] = row_data['Tags']['_scopeId']
            data['gameid'] = row_data['Tags']['_projectId']
            play_history_schema = PlayHistorySchema()
            play_history = play_history_schema.load(data)
            play_history.create()
            print("==========================PlayHistory成功建立==========================")    

        # Store EyeTracking Data
        if row_data['Name'] == 'LabData.EyePositionData':
            print("==================正在儲存眼動資料到DB中")
            data['gameid'] = row_data['Tags']['_projectId']
            data['username'] = row_data['Tags']['_userId']
            data['sessionid'] = row_data['Tags']['_scopeId']
            tags_data = json.loads(row_data['Tags']['data'])
            data['mode'] = tags_data['mode']
            data['time_stamp'] = tags_data['timeStamp']
            data['position_x'] = tags_data['positionX']
            data['position_y'] = tags_data['positionY']
            data['position_z'] = tags_data['positionZ']
            data['openness_left'] =tags_data['leftEyeOpenness']
            data['openness_right'] = tags_data['rightEyeOpenness']
            eyeTracking_schema = EyeTrackingDataSchema()
            eyeTracking = eyeTracking_schema.load(data)
            eyeTracking.create()
            mode = tags_data['mode']

        # End Play History
        elif row_data['Name'] == 'DataSync.Entity.ScopeEndEntity':
            X = []
            Y = []
            winkGateL = True #張開眼睛:True
            winkGateR = True #張開眼睛:True
            winkTimesL = 0
            winkTimesR = 0
            gameTime = -1
            eyePositionGate = True
            count = 0
            dist = 0
            feature = {}
            print("沒有data啦 收完了啦")

            #eye-tracking data feature calculate
            query = EyeTrackingData.query.filter_by(gameid=row_data['Tags']['_projectId'], sessionid=row_data['Tags']['_scopeId'], username=row_data['Tags']['_userId'])
            for raw_data in query:
                
                if(eyePositionGate): #如果遊戲時間間隔大於0.05秒就記錄眼動位置(放大10倍比較好畫圖)
                    if raw_data.position_x *10 != 0.0:
                        X.append((raw_data.position_x)*10)
                        Y.append((raw_data.position_y)*10)
                        eyePositionGate = False #眼動位置紀錄完記得把開關關掉
                    #print("==========眼動位置紀錄==========")
                    
                if raw_data.time_stamp-gameTime >= 0.05: #將現在遊戲時間與上次紀錄眼動參數的時間相減 找個間格時間(0.05s)當輸出條件
                    gameTime = raw_data.time_stamp
                    eyePositionGate = True #眼動位置紀錄開關打開

                if raw_data.openness_left == 0.0:
                    winkGateL = False #閉上眼睛變成False
                elif winkGateL == False and raw_data.openness_left == 1.0:
                    winkGateL = True
                    winkTimesL = winkTimesL+1
                    #print("==========左眼眨眼啦==========")

                if raw_data.openness_right == 0.0:
                    winkGateR = False #閉上眼睛變成False
                elif winkGateR == False and raw_data.openness_right == 1.0:
                    winkGateR = True
                    winkTimesR = winkTimesR+1
                   # print("==========右眼眨眼啦==========")
            
            print( "現在有幾個X點R:", len(X), "======================X: ", X) 
            print( "現在有幾個Y點R:", len(Y), "======================Y: ", Y)     

            #picture output  
            plt.plot(X,Y)
            plt.ylabel('Y axis')
            plt.xlabel('X axis')
            sesson_id = row_data['Tags']['_scopeId']
            plt.savefig(f'./static/{sesson_id}.jpg')

            while(True): #計算眼動總距離與速度
                print("======================X[count]: ", X[count])
                dist = dist + math.sqrt((X[count]-X[count+1])**2+(Y[count]-Y[count+1])**2)
                if count != len(X)-2:
                    count=count+1
                else:
                    break
            print("feature: ",dist, gameTime, dist/gameTime, winkTimesL, winkTimesR)
            feature['gameid'] = row_data['Tags']['_projectId']
            feature['username'] = row_data['Tags']['_userId']
            feature['sessionid'] = row_data['Tags']['_scopeId']
            feature['mode'] = mode
            feature['tracking_dist'] = dist
            feature['game_time'] = gameTime
            feature['tracking_speed'] = dist/gameTime
            feature['wink_left'] = winkTimesL
            feature['wink_right'] = winkTimesR
            eyeTrackingFeature_schema = EyeTrackingFeatureSchema()
            eyeTracking = eyeTrackingFeature_schema.load(feature)
            eyeTracking.create()
                
        #     return response_with(resp.SUCCESS_201)
        # except Exception as e:
        #     print(e)
        #     return response_with(resp.INVALID_INPUT_422)

    return 'OK'