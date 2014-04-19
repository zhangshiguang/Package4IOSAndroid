#!/usr/bin/python
# coding=utf-8
# author：jordan QQ87895224 zzsg2005@126.com 
#此脚本在使用时需注意 JDK 环境， 及 Android Build-tools PATH
#  如：export PATH=/Users/apple/adt-bundle-mac/sdk/build-tools/19.0.0:$PATH 

##找个时间优化：可以自动判断java版本；

##2014-03-03版
#打包步骤
#1.使用eclipse （java V1.6）导出signed package 叫jordan.apk，放到当前目录下；
#  签名文件放到./keystore/ 下；
#  当前目录下 配置好channel文件；格式 “ch=渠道编号,渠道名”；
#  当前目录下 重新修改编译的apktool1.5.3.jar （见4）；  
#2.检查控制台java版本，也要是1.6版。  控制台和eclipse必须使用相同版本的java；
#3.在当前目录下，准备好 AndroidManifest.xml,即 CHANNEL_VAL对应值是“ch=0000000” ，UMENG_CHANNEL对应值是"default"。
#4.因为apk中包含了百度分享使用的com目录，导致我（jordan）下载了apktool源代码，修改了解包后的复制过程代码，增加了复制com目录；
#5. 我（jordan）编译出来的apktool是apktool1.5.3.jar；
#   再执行脚本，打出bin下各个渠道包。

import os
import shutil
import time
from datetime import date       
from shutil import copytree
import logging
import glob
import gzip
import zipfile


#读取友盟通道号文件
def readChannelValfile(filename):
    f = file(filename)
    while True:
        line = f.readline().strip()
        if len(line) == 0:
            break
        else:
            channelValList.append(line);
    f.close()    
    
    
#检查配置
def checkManifest():
		chflag=0
		umflag=0
		if (os.path.exists('./AndroidManifest.xml') == False):
			print 'auto config ./AndroidManifest.xml'
			shutil.copyfile("./temp/AndroidManifest.xml", './AndroidManifest.xml')
		else:
			f = file('./AndroidManifest.xml')
			for line in f:
				if line.find('ch=0000000') > 0:
					chflag=1
				if line.find('default') > 0:
					umflag=1
			f.close()
			
			
			if chflag !=1 or umflag !=1 :
				print '---------./AndroidManifest.xml 配置有错,启动自动配置...'
				
				f = file('./AndroidManifest.xml')
				tmpXML=''
				for line in f:
					if line.find('CHANNEL_VAL') > 0:
						chflag=1
						line = '        <meta-data android:name="CHANNEL_VAL" android:value="ch=0000000" />'
					if line.find('UMENG_CHANNEL') > 0:
						umflag=1
						line = '        <meta-data android:name="UMENG_CHANNEL" android:value="default" />'
					tmpXML += line	
				f.close()
				output = open('./AndroidManifest.xml', 'w')
				output.write(tmpXML)
				output.close()

          
#修改友盟通道号
#./temp/AndroidManifest.xml
def modifyChannel(value):
		tempXML = ''
		chValue,umengValue = value.split(",")
		print chValue 
		print umengValue
		f = file('./AndroidManifest.xml')
		for line in f:
				if line.find('ch=0000000') > 0:
					line = line.replace('ch=0000000', chValue)
				if line.find('default') > 0:
					line = line.replace('default', umengValue)
				tempXML += line
		f.close()
 
		output = open('./temp/AndroidManifest.xml', 'w')
		output.write(tempXML)
		output.close()

		unsignApk = r'%s_%s_unsigned.apk'% (easyName, umengValue)
		cmdPack = r'java -jar apktool1.5.3.jar b temp ./bin/%s'% (unsignApk)
		print cmdPack
		os.system(cmdPack)
    
		signedjar = r'./bin/%s_%s.apk'% (easyName, umengValue)
		unsignedjar = r'./bin/%s'% (unsignApk)         
    ## JDK 1.7
		cmd_sign = r'jarsigner -digestalg SHA1 -sigalg MD5withRSA -verbose -keystore %s -storepass %s -signedjar %s %s %s'% (keystore, storepass, signedjar, unsignedjar, alianame)
    ## 此脚本在 JDK 1.6 使用时 删除此参数======>>>>  “-digestalg SHA1 -sigalg MD5withRSA”
		#cmd_sign = r'jarsigner -verbose -keystore %s -storepass %s -signedjar %s %s %s'% (keystore, storepass, signedjar, unsignedjar, alianame)
		os.system(cmd_sign)
		os.remove(unsignedjar)
    
		#align 
		aligned_apk = r'%s_%s_%s.apk'% (easyName,umengValue,date.today().isoformat())
		cmd_align = r'zipalign -v 4 %s ./bin/%s'% (signedjar,aligned_apk)    
		os.system(cmd_align)
		os.remove(signedjar)



channelList = []         
#签名的apk文件 默认文件名
apkName = 'jordan.apk'
#自动找到当前目录下第一个jordan*.apk文件
listf=glob.glob("jordan*.apk")
if  listf :
	for f in listf:
		print f
else:
	print "must have a jordan*.apk file."
	sys.exit()
	
for s in listf:
	if s.find("jordan")==0:
		apkName = s
		break;
print r'we select %s' % (apkName)
#

easyName = apkName.split('.apk')[0]
#签名文件
keystore='./keystore/Androidjordan.keystore'
#签名文件密钥
storepass='123321'
#签名文件别名
alianame='jordan'

output_apk_dir="./bin"
if os.path.exists(output_apk_dir):
    shutil.rmtree(output_apk_dir)

readChannelfile('./channel')
print '-------------------- your channel values --------------------'
print 'channel list: ', channelList
#####使用apktool解包一次
cmdExtract = r'java -jar apktool1.5.3.jar  d -f -s %s temp'% (apkName)
print cmdExtract
os.system(cmdExtract)
                 
checkManifest()
for channel in channelList:
    modifyChannel(channel)

if os.path.exists('./temp'):
	shutil.rmtree('./temp')
if os.path.exists('./AndroidManifest.xml'):
	os.remove('./AndroidManifest.xml')
print '-------------------- Done --------------------'

