# AdvertisingClassification

First Mini Project  

목록 | 설명
------------|--------------------
[blog.py](https://github.com/Yeons2013/AdvertisingClassification/blob/master/blog.py) | 크롤링 코드 모듈화
[DataGet.ipynb](https://github.com/Yeons2013/AdvertisingClassification/blob/master/DataGet.ipynb) | blog.py 실행코드
[Train.ipynb](https://github.com/Yeons2013/AdvertisingClassification/blob/master/Train.ipynb) | 전처리 및 모델학습
[nsmc_stopwords_5차.txt](https://github.com/Yeons2013/AdvertisingClassification/blob/master/nsmc_stopwords_5%EC%B0%A8.txt) | 불용어 사전




###
### 텍스트마이닝&ML을 이용해 블로그 광고글 구분하기

---

### 1. 프로젝트 목적
- 많은 블로그 체험 후기글이 사실은 돈을 받고 쓴 광고글이고 이로 인해 블로그 글에 대한 신뢰성이 하락함.
- 텍스트 마이닝과 ML을 통해 광곡글을 구분하고 블로그 글에 대한 신뢰성을 회복시키고 소비자의 현명한 소비를 도움.

---
### 2. 프로젝트 기간
- 22.07.13 ~ 22.08.04

---
### 3. 광고글과 비광고글의 경향 파악
<img src="https://media.discordapp.net/attachments/1022477080031666276/1061545087286394950/image.png?width=1202&height=676">
<img src="https://media.discordapp.net/attachments/1022477080031666276/1061545427243110530/image.png?width=1202&height=676">

(해당 패턴을 바탕으로 수집한 데이터에 라벨링 작업 진행)

---
### 4. 데이터 수집

크롤링 실행 : DataGet.ipynb

**Step1.** 크롤링 클래스 객체 선언
```python
food = blog_restaurants()
```

```python
지역을 입력해주세요 : 부산 해운대
```

**Step2.** 키워드에 해당하는 지역 맛집 게시글 크롤링

ex) '부산 해운대 맛집' 키워드로 작성된 블로그 글 크롤링
```
food.blog_restaurant_get()
```
<img src="https://media.discordapp.net/attachments/1022477080031666276/1061553847971106876/image.png">

**Step3.** 크롤링된 게시글에 언급된 식당명 리스트에 추가
```
food.blog_restaurant_get()
```

**Step4.** 게시글이 가장 많이 작성된 식당 10개 선별
```
food.top_10_restaurant_get()
```

**Step5.** 10개의 식당에 대한 후기글 크롤링 후 저장
```
food.restaurant_get()
```
<img src="https://media.discordapp.net/attachments/1022477080031666276/1061555578050195586/image.png?width=1202&height=676">



---
### 5. 전처리
+ Null 값 및 중복값 확인 및 제거
```
data.dropna(inplace=True)
data = data.drop_duplicates(['body'],keep='first')
```
+ 정규 표현식을 활용해 한글 및 공백을 제외한 문자 제거
+ 한글 형태소 분석기인 Okt를 활용해 형태소 토큰화 및 품사태깅
+ 불용어사전 작성 및 불용어 제거(불용어사전 : ['nsmc_stopwords_5차.txt'](https://github.com/Yeons2013/AdvertisingClassification/blob/master/nsmc_stopwords_5%EC%B0%A8.txt))
+ 광고 글 구분에 유의미한 명사, 형용사, 동사를 제외한 품사 제거
```
def preprocessing(review):
    okt = Okt()
    
    f = open('nsmc_stopwords_5차.txt')
    stop_words = f.read().split()
    
    # 1. 한글 및 공백을 제외한 문자 모두 제거. → 한글 이외의 문자는 광고 구분에 중요하지 않다고 판단
    review_text = re.sub("[^가-힣\\s]", "", review)
    
    # 2. okt 객체를 활용해서 형태소 토큰화 + 품사 태깅
    word_review = okt.pos(review_text, stem=True)

    # 3. 노이즈 & 불용어 제거 → 광고 구분에 유의미한 토큰을만을 선별하기 위한 작업(불용어 사전 개수 22,678개)
    word_review = [(token, pos) for token, pos in word_review if not token in stop_words and len(token) > 1]
 
    # 4. 명사, 동사, 형용사 추출
    word_review = [token for token, pos in word_review if pos in ['Noun', 'Verb', 'Adjective']]
    
    return word_review
```
+ Standard Scaler를 활용해 본문을 제외한 나머지 특성(ex>이미지개수, 스티커수, 문장길이..) 표준화 작업
```
from sklearn.preprocessing import StandardScaler

ss = StandardScaler()
ss.fit(train_input2)

train_scaled2 = ss.transform(train_input2)
test_scaled2 = ss.transform(test_input2)
```
+ TfidfVectorizer를 활용한 본분 인코딩 작업
```
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

tfidf = TfidfVectorizer(tokenizer=preprocessing, max_features=2500, min_df=25, max_df=0.5) 

train_input_tfidf = tfidf.fit_transform(train_input)
```

---
### 6. ML 모델 학습
#### (1) 본문을 제외한 나머지 특성만으로 학습
<img src="https://media.discordapp.net/attachments/1022477080031666276/1061564995063795752/image.png?width=1202&height=676">

#### ※ 사용 모델
**① RandomForestClassifier**

◆ 선정이유
+ 과대적합 문제 최소화하여 모델의 정확도 향상
+ 대용량 데이터 처리에 효과적
+ Classification 및 Regression 문제에 모두 사용 가능

**② ExtraTreesClassifier**

◆ 선정이유
+  feature중에 아무거나 고른 다음 그 feature에 대해 최적의 Node를 분할
+ 준수한 성능을 보이며 과대적합을 막고 검증 세트의 점수를 높이는 효과가 있음.
+ 속도가 빠르다는 장점이 있음.
<img src="https://media.discordapp.net/attachments/1022477080031666276/1061568202531934268/image.png">

#### 　　　　
##
#### (2) 본문 이외의 특성을 토큰으로 만들어 본문 하단에 삽입 후 본문만으로 학습
<img src="https://media.discordapp.net/attachments/1022477080031666276/1061570872068018196/image.png?width=1202&height=676">

#### ※ 사용 모델
RandomForestClassifier, ExtraTreesClassifier이외에 추가로 2개 더 선정

**③ LogisticRegression**

◆ 선정이유
+ 로지스틱 회귀는 매우 효율적이고 엄청난 양의 계산 리소스를 필요로 하지 않기 때문에 널리 사용됨.
+ 쉽게 구현되고 학습하기 쉬우므로 다른 복잡한 알고리즘의 성능을 측정하는 데 도움이 되는 훌륭한 기준이 됨.

**④ *AdaBoostClassifier**

◆ 선정이유
+ AdaBoost는 구현하기 쉬움.
+ 약한 분류기의 실수를 반복적으로 수정하고 약한 학습자를 결합하여 정확도를 높임.
+ andomForest와 비교하였을 때 대체로 boosting이 속도가 더 빠르고 결과가 더 좋게 나옴.
<img src="https://media.discordapp.net/attachments/1022477080031666276/1061574330611413072/image.png">


---
### 7. 성능 개선 시도
#### (1) GridSearchCV를 활용한 Hyper-Parameter Tuning
※ GridSearchCV : ML에서 모델의 성능을 높이기 위한 기법 중 하나. 사용자가 직접 모델의 Hyper-Parameter 값을 리스트로 입력하면, 값에 대한 경우의 수 마다 예측 성능을 측정 평가하여 비교하면서 최적의 Hyper-Parameter 값을 찾는 과정을 진행.
<img src="https://media.discordapp.net/attachments/1022477080031666276/1061577180393504838/image.png?width=935&height=676">
#### ★ 리스트 값을 지속적으로 바꿔주면서 최적의 조합을 찾음

#
#### (2) Ensemble(Voting)을 통해 성능 개선
◆ SoftVoting(다수의 classifier의 예측 결과값간 확률을 평균하여 최종 class를 결정)
<img src="https://media.discordapp.net/attachments/1022477080031666276/1061578549154287646/image.png">

◆ Hard Voting(다수의 classifier의 예측 결과값을 다수결로 최종 class를 결정)
<img src="https://media.discordapp.net/attachments/1022477080031666276/1061579110402502776/image.png">
#### (Soft Voting 시 더 높은 성능을 보였음.)

# 
#### (3) 본문 이외의 특성으로 학습한 모델, 본문만으로 학습한 모델 Voting 후 Score
<img src="https://media.discordapp.net/attachments/1022477080031666276/1061580072978489464/image.png">


---
### 8. 결과 분석 및 한계점
**(1) 한계점**
+ 주관적으로 설정한 기준을 바탕으로 라벨링 작업을 진행했기 때문에 라벨링에 대한 신뢰성에 한계가 있음.
+ 데이터로 사용한 네이버 블로그 글의 경우 실제 후기글처럼 속인 교묘한 광고글이 많아 분류하기가 어려움.
+ 카운트를 기반으로 한 텍스트 마이닝&ML Model의 한계점(문장의 순서정보를 반영하지 못함)

**(2) 긍정적인 점**
+ 불용어 제거와 같은 노동력이 투입된 전처리 작업으로 성능을 끌어올림.
+ 다양한 ML Model을 학습해봄.
+ GridSearchCV, Voting과 같은 기술을 활용해 성능 개선을 시도해봄.

