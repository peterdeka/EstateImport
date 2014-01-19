import pymysql
import ftplib
import requests
import consts as cc
import unicodedata
import io
from ftplib import FTP
from PIL import Image
import os
import random

def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')

conn = pymysql.connect(host='new.wannaup.com', port=3306, user='beast', passwd=cc.sqlpass, db=cc.sqldb)


def get_alias(t):
	t=strip_accents(t)
	t=t.replace("'",'')
	t=t.replace(' ','-')
	t=t.lower()
	return t

def add_apt(apt):
	apt['vacationrentals_desc']=apt['vacationrentals_desc'].replace(u'\u2019', "\'")
	cur = conn.cursor()
	#ottengo rgt e lft
	S_rg_lt='SELECT * FROM '+cc.sqlprefix+'assets WHERE parent_id='+cc.jome_parentid+' ORDER BY id DESC LIMIT 1'
	cur.execute(S_rg_lt)
	a=cur.fetchone()
	lft=a[2]
	rgt=a[3]
	lft=int(rgt)+1
	rgt=str(lft+1)
	lft=str(lft)
	itemn=a[5].split('.')
	itemn=str(int(itemn[len(itemn)-1])+1)
	S_addr="SELECT * FROM "+cc.sqlprefix+"cddir_categories WHERE extension='com_jomcomdev.address' AND title='"+apt['category_name']+"'"
	print S_addr
	cur.execute(S_addr)
	a=cur.fetchone()
	if not a:
		print 'address ',apt['category_name'],' not found'
		return False
	addr_id=str(a[0])
	
	#add asset
	I_asset="INSERT INTO "+cc.sqlprefix+"assets VALUES(NULL,"+cc.jome_parentid+","+lft+","+rgt+",2,"+'"com_jomestate.item.'+itemn+'","'+apt['vacationrentals_name']+'","")'
	cur.execute(I_asset)
	asset_id=str(conn.insert_id())
		
	#add jome content
	sqlnone='NULL'
	
	I_je_cont="INSERT INTO "+cc.sqlprefix+"cddir_jomestate VALUES("+sqlnone+","+cc.jome_cat_rent+","+cc.jome_cat_type+","+addr_id+","+cc.jome_user_id+","+cc.jome_comp_id+","
	I_je_cont+=cc.jome_agent_id+","+asset_id+",0,'"+apt['vacationrentals_name']+"','"+get_alias(apt['vacationrentals_name'])+"','',"+'"<p>'+apt['vacationrentals_desc'].split('.')[0]+'</p>",'
	I_je_cont+='"<p>'+apt['vacationrentals_desc']+'</p>"'+",'A','','0',now(),now(),now(),"+sqlnone+',1,1,0,"'+apt['vacationrentals_name']+'","'+apt['vacationrentals_desc'].split('.')[0]+'",0,0,'+sqlnone+",'*')"
	print I_je_cont
	cur.execute(I_je_cont)

	#fields
	je_apt_id=str(conn.insert_id())
	I_je_h_fields="INSERT INTO "+cc.sqlprefix+"cddir_content_has_fields VALUES(NULL,"+je_apt_id+",1,NULL,'"+apt['feature_bathroom']+"',NULL)"
	cur.execute(I_je_h_fields)
	I_je_h_fields="INSERT INTO "+cc.sqlprefix+"cddir_content_has_fields VALUES(NULL,"+je_apt_id+",2,NULL,'"+apt['feature_bedroom']+"',NULL)"
	cur.execute(I_je_h_fields)
	I_je_h_fields="INSERT INTO "+cc.sqlprefix+"cddir_content_has_fields VALUES(NULL,"+je_apt_id+",3,'"+apt['feature_garage']+"',NULL,NULL)"
	cur.execute(I_je_h_fields)
	I_je_h_fields="INSERT INTO "+cc.sqlprefix+"cddir_content_has_fields VALUES(NULL,"+je_apt_id+",5,NULL,'',NULL)"
	cur.execute(I_je_h_fields)
	I_je_h_fields="INSERT INTO "+cc.sqlprefix+"cddir_content_has_fields VALUES(NULL,"+je_apt_id+",6,0,NULL,NULL)"
	cur.execute(I_je_h_fields)
	ameni=apt['feature_amenities'].split(',')
	strout='<ul>'
	for a in ameni:
		strout+='<li>'+a+'</li>'
	ameni=apt['feature_other_facilities'].split(',')
	for a in ameni:
		strout+='<li>'+a+'</li>'
	strout+='</ul>'

	I_je_h_fields="INSERT INTO "+cc.sqlprefix+"cddir_content_has_fields VALUES(NULL,"+je_apt_id+",9,NULL,'"+strout+"',NULL)"
	cur.execute(I_je_h_fields)

	I_je_price="INSERT INTO "+cc.sqlprefix+"cddir_prices VALUES(NULL,"+je_apt_id+","+cc.jome_rentalprice_id+",'com_jomestate',"+apt['vacationrentals_price']+",NULL)"
	cur.execute(I_je_price)
	

	#aggiungo foto
	upload_images(apt,je_apt_id,apt['vacationrentals_image'])
	conn.commit()
	return True


def upload_images(apt,apt_id,urls):
	ftp=FTP()
	ftp.connect(cc.FTP_HOST,port=cc.FTP_PORT)
	ftp.login("wannaftp", "Xa!Hu7Pe")
	
	i=0
	for u in urls.split(','):
		ftp.cwd(cc.FTP_DIR)
		f = open('tmp','wb')
		imgurl=cc.IMAGE_URL+u
		print "getting image",imgurl
		f.write(requests.get(imgurl).content)
		print "got image"
		f.close()
		path=cc.jome_imgdirs[random.randrange(0, len(cc.jome_imgdirs))]
		ftp.cwd(path)
		fname=get_alias(apt['vacationrentals_name'])+'-'+str(i)+'.'+u.split('.')[len(u.split('.'))-1]
		print "uploading image to ",fname
		f=open('tmp','r')
		ftp.storbinary('STOR '+fname,f)
		f.close()
		i+=1
		#add db entry
		img = Image.open('tmp')
		width, height = img.size
		cur = conn.cursor()
		print "adding image db entry"
		if i<3:
			I_img="INSERT INTO "+cc.sqlprefix+"cddir_images VALUES(NULL,"+apt_id+',NULL,NULL,40,"'+apt['vacationrentals_name']+'","'+fname+'","'+path+'",'+str(width)+","+str(height)+','+str(i)+',"",'+str(os.path.getsize('tmp'))+',"com_jomestate")'
		else:
			I_img="INSERT INTO "+cc.sqlprefix+"cddir_images VALUES(NULL,"+apt_id+',NULL,NULL,41,"'+apt['vacationrentals_name']+'","'+fname+'","'+path+'",'+str(width)+","+str(height)+','+str(i)+',"",'+str(os.path.getsize('tmp'))+',"com_jomestate")'
		cur.execute(I_img)






