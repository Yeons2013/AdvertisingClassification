import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from urllib.parse import quote_plus
from urllib.parse import unquote_plus




# 식당 크롤링 클래스
class blog_restaurants:
  def __init__(self) :
    self.restaurant_blog_title = []
    self.naver_restaurants = []
    self.top_10_restaurant = []
    self.key = input('지역을 입력해주세요 : ')

#객체를 생성하면서 입력한 지역에 대한 맛집 검색 글 7000개의 제목을 가져옴
  def blog_restaurant_get(self,kind='맛집'):    
    key = '{} {} 추천'.format(self.key,kind)
    key_encoded = quote_plus(key) 
    url_list = []
    pre_resp_content = ''
    for i in range(1,1001):
      url = 'https://section.blog.naver.com/ajax/SearchList.naver?countPerPage=7&currentPage={}&endDate=&keyword={}&orderBy=sim&startDate=&type=post'.format(i,key_encoded)
      headers = {
          'referer' : 'https://section.blog.naver.com/Search/Post.naver?pageNo={}&rangeType=ALL&orderBy=sim&keyword={}'.format(i,key_encoded),    
          'user-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
      }
      resp = requests.get(url, headers=headers)
      if pre_resp_content == resp.content :
        break
      data = json.loads(resp.text[6:-2])     
      re = data['result']['searchList']
      for i in re:
        url_list.append(i['postUrl'])      
      pre_resp_content = resp.content

    for i in range(len(url_list)) :
      url = url_list[i]
      resp = requests.get(url)
      soup = BeautifulSoup(resp.content, 'lxml')
      ifr = soup.select('iframe') 
      re = ifr[0]['src'] 
      url = 'https://m.blog.naver.com{}'.format(re) 

      resp = requests.get(url)
      soup = BeautifulSoup(resp.content, 'lxml')

      if soup.select('div.tit_area h3') :          
        title_tags = soup.select('div.tit_area h3')
      elif soup.select('div.se-module.se-module-text.se-title-text p span') :
        title_tags = soup.select('div.se-module.se-module-text.se-title-text p span')  
      elif soup.select('div.se_editView.se_title div h3'):         
        title_tags = soup.select('div.se_editView.se_title div h3')
      else :
        title_tags = url      

      if title_tags == url:
        self.restaurant_blog_title.append(title_tags)
      else :
        self.restaurant_blog_title.append(title_tags[0].text)


# 네이버에 등록된 해당지역 식당을 모두 가져옴
  def naver_restaurants_get(self):
    key = '{} 식당'.format(self.key)
    keyword = quote_plus(key)
    cnt = 1 

    while True : 
      url ='https://map.naver.com/v5/api/search?caller=pcweb&query={}&type=all&searchCoord=127.4375232;36.3064369&page={}&displayCount=50&isPlaceRecommendationReplace=true&lang=ko'.format(keyword,cnt)

      headers = {
          'referer' : 'https://map.naver.com/',
          'cookie' : 'NNB=TP5EWDLX5SAWE; _ga_7VKFYR6RV1=GS1.1.1653825346.1.1.1653825474.25; _gcl_au=1.1.1752887798.1654272178; _fbp=fb.1.1654272178308.1120301041; ASID=788e25eb0000018148c95a3b000000ee; _ga=GA1.1.341588366.1653825347; _ga_1BVHGNLQKG=GS1.1.1654861422.1.1.1654861745.0; nx_ssl=2; page_uid=hWXxIsprvhGssekoQtsssssstYK-154436; _naver_usersession_=ABwC0Ztrgy+qwSQ0qFxytQ==; page_uid=a2a10af0-5796-43e4-a7d2-ee11facbb056',
          'user-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
          }

      resp = requests.get(url, headers=headers)
      data = json.loads(resp.text)
      if data == {'error': {'code': 'XE400', 'msg': 'Bad Request.', 'displayMsg': '잘못된 요청입니다.', 'extraInfo': None}} :
        break
      else :
        res_list = data['result']['place']['list']

      for re in res_list :
        self.naver_restaurants.append(re['name'])    

      cnt += 1
 


# 네이버에 등록된 식당이름으로 작성된 글이 얼마나 있나 찾아서 10위까지 순위를 매김.
  def top_10_restaurant_get(self):
    res_match = []
    for i in self.restaurant_blog_title :
      for j in self.naver_restaurants :
        if i.find(j) != -1 :
          res_match.append(j)
        elif i.find(j.strip()) != -1 :
          res_match.append(j)


    res_match.sort()

    set_res = set(res_match)
    list_res = list(set_res)

    doc_count = {}
    for i in list_res :
      doc_count[i] = res_match.count(i)


    res_count = sorted(doc_count.items(),key=lambda x : x[1], reverse=True)
    self.top_10_restaurant.append(res_count[0:10])






#검색된 1~10위의 식당 후기글을 1400개씩 크롤링해서 CSV로 저장.
  def restaurant_get(self):

    key_list = self.top_10_restaurant[0]

    title_list = []
    text_list = []
    url_list = []
    img_list = []
    sticker_list = []
    map_list = []
    video_list = []
    body_len_list = []
    label_list = []



    for idx, k in enumerate(key_list) :
      key = '{} {} 후기'.format(self.key,k[0])
      key_encoded = quote_plus(key) 


      im_list = []
      txt_list = []  
      sti_list = []
      ma_list = []  
      vid_list = []
            

      pre_resp_content = ''
      for num in range(10,211):
        url = 'https://section.blog.naver.com/ajax/SearchList.naver?countPerPage=7&currentPage={}&endDate=&keyword={}&orderBy=sim&startDate=&type=post'.format(num,key_encoded)

        headers = {
            'referer' : 'https://section.blog.naver.com/Search/Post.naver?pageNo={}&rangeType=ALL&orderBy=sim&keyword={}'.format(num,key_encoded),    
            'user-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
        }

        resp = requests.get(url, headers=headers)
        if pre_resp_content == resp.content :
          break
        data = json.loads(resp.text[6:-2])
        re = data['result']['searchList']
        for i in re:
          url_list.append(i['postUrl'])

        pre_resp_content = resp.content

      for i in range(len(url_list)) : 
        url = url_list[i]
        resp = requests.get(url)
        soup = BeautifulSoup(resp.content, 'lxml')
        ifr = soup.select('iframe') 
        re = ifr[0]['src'] 

        url = 'https://m.blog.naver.com{}'.format(re) 

        resp = requests.get(url)
        soup = BeautifulSoup(resp.content, 'lxml')

        if soup.select('div.tit_area h3') :          
          title_tags = soup.select('div.tit_area h3')
        elif soup.select('div.se-module.se-module-text.se-title-text p span') :
          title_tags = soup.select('div.se-module.se-module-text.se-title-text p span')  
        elif soup.select('div.se_editView.se_title div h3'):         
          title_tags = soup.select('div.se_editView.se_title div h3')
        else :
          title_tags = url
          
          
        if soup.select('div.se-main-container div div div div p span') :                
          text_tags = soup.select('div.se-main-container div div div div p span')                  
        elif soup.select('div.post_ct div span') :
          text_tags = soup.select('div.post_ct div span') 
        elif soup.select('div.post_ct p span') :
          text_tags = soup.select('div.post_ct p span')                
        else :
          text_tags = url   


        if soup.select('div.post_ct img') :
          img_tags = soup.select('div.post_ct img')
        else :
          img_tags = 0

        if soup.select('div.post_ct img._sticker_img') :
          sticker_tags = soup.select('div.post_ct img._sticker_img')
        elif soup.select('div.se-module.se-module-sticker img') :
          sticker_tags = soup.select('div.se-module.se-module-sticker img')
        else :
          sticker_tags = 0


        if soup.select('div.se-module.se-module-map-image') :
          map_tags = soup.select('div.se-module.se-module-map-image')
        else :
          map_tags = 0


        if soup.select('div.se-section.se-section-video.se-section-align-.se-l-default div.se-module.se-module-video') :
          video_tags = soup.select('div.se-section.se-section-video.se-section-align-.se-l-default div.se-module.se-module-video')        
        elif soup.select('span._naverVideo._vnl') :
          video_tags = soup.select('span._naverVideo._vnl')
        elif soup.select('div.se-section.se-section-video.se-section-align-left.se-l-default div.se-module.se-module-video.__se-component') :
          video_tags = soup.select('div.se-section.se-section-video.se-section-align-left.se-l-default div.se-module.se-module-video.__se-component')
        else :
          video_tags = 0


        if title_tags == url :                                   
          title_list.append(title_tags)                            
        else :
          title_list.append(title_tags[0].text)                 
        
        if text_tags == url:                                      
          text_list.append(text_tags)
          body_len_list.append(0)
        else :                                              
          for tex in text_tags :                       
            txt_list.append(tex.text)                                     
          new_text = ','.join(txt_list)                                 
          text_list.append(new_text.replace(',\u200b',''))
          body_len_list.append(len(new_text.replace(',\u200b','')))


        if img_tags == 0 :                                      
          img_list.append(img_tags)
        else :                                          
          for img in img_tags :                       
            im_list.append(img['src'])
          img_list.append(len(im_list))
          
        if sticker_tags == 0 :                                      
          sticker_list.append(sticker_tags)
        else :                                          
          for sti in sticker_tags :                       
            sti_list.append(sti)
          sticker_list.append(len(sti_list))

        if map_tags == 0 :                                      
          map_list.append(map_tags)
        else :                                          
          for map in map_tags :                       
            ma_list.append(map)
          map_list.append(len(ma_list))


        if video_tags == 0 :                                      
          video_list.append(video_tags)
        else :                                          
          for video in video_tags :                       
            vid_list.append(video)
          video_list.append(len(vid_list))



        if img_list[i] < 5 :
          text_list[i] += ' 겸뱍'
        
        if body_len_list[i] < 800 :
          text_list[i] += ' 쓰탤'
        
        if img_list[i] > 25 :
          text_list[i] += ' 낟쭘'
        elif img_list[i] > 15 :
          text_list[i] += ' 덩셤'
        elif img_list[i] >= 8 :
          text_list[i] += ' 횡뤼'
        else :
          text_list[i] += ' 샹륨'

        
        if video_list[i] > 0 :
          text_list[i] += ' 굇묜'
        
        if text_list[i].count(k[0]) > 4 :
          text_list[i] += ' 뉠튠'
        
        if map_list[i] > 0 :
          text_list[i] += ' 썅꽜'
        
        if img_list[i] < 5 :
          text_list[i] += ' 겸뱍'
        
        if sticker_list[i] > 5 :
          text_list[i] += ' 춥륄'
        


        

        if text_list[i].count('소정의') > 0 or text_list[i].count('원고료') > 0 or text_list[i].count('문의') > 0 or text_list[i].count('업체') > 0 :
          label_tag = 1
        elif img_list[i] < 8 :
          label_tag = 0          
        elif img_list[i] <= 15 and body_len_list[i] < 800 :
          label_tag = 0 
        elif img_list[i] > 25 and body_len_list[i] < 200 :
          label_tag = 1
        elif img_list[i] > 15 and map_list[i] > 0 and video_list[i] > 0 and text_list[i].count(k[0]) > 4 :
          label_tag = 1
        elif text_list[i].count('내돈내산') > 0 or text_list[i].count('비싸다') > 0 or text_list[i].count('짜다') > 0 or text_list[i].count('덥다') > 0 or text_list[i].count('불친절') > 0 or text_list[i].count('짜증') > 0 or text_list[i].count('후회') > 0 or text_list[i].count('극혐') > 0 or text_list[i].count('스트레스') > 0 or text_list[i].count('아쉽다') > 0 or text_list[i].count('나쁘다') > 0 :
          label_tag = 0
        elif img_list[i] > 15 and text_list[i].count('전화번호') > 0 or text_list[i].count('댓글') > 0 or text_list[i].count('영업시간') > 0 or text_list[i].count('이웃') > 0 or text_list[i].count('전화번호') > 0 or text_list[i].count('브레이크타임') > 0 or text_list[i].count('찾아오는길') > 0 or text_list[i].count('운영시간') > 0 :
          label_tag = 1     
        elif img_list[i] > 15 and sticker_list[i] > 5 :
          label_tag = 1
        elif img_list[i] > 25 and map_list[i] > 0:
          label_tag = 1
        else :
          label_tag = 0

        label_list.append(label_tag)


        txt_list.clear()  
        im_list.clear()
        sti_list.clear()  
        ma_list.clear()                         
        vid_list.clear()

      doc = {
          'title' : title_list,
          'body' : text_list,
          'img' : img_list,
          'sticker' : sticker_list,
          'map' : map_list,
          'video' : video_list,
          'body_len' : body_len_list,
          'label' : label_list
      }

      df = pd.DataFrame(doc)
      df.to_csv('{}위 {}.csv'.format(idx+1, key))

      title_list.clear()
      text_list.clear()
      url_list.clear()
      img_list.clear()
      sticker_list.clear()
      map_list.clear()
      video_list.clear()
      body_len_list.clear()
      label_list.clear()



