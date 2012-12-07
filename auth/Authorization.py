#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from models import *
from S3Error import *
import base64
import time
import hmac
from s3db.s3service import S3Service
from s3db.s3model import S3User
try:
    from hashlib import sha1  # for python2.4
    from hashlib import sha256 as sha256
    
    if sys.version[:3] == "2.4":
        # we are using an hmac that expects a .new() method.
        class Faker:
            def __init__(self, which):
                self.which = which
                self.digest_size = self.which().digest_size
            
            def new(self, *args, **kwargs):
                return self.which(*args, **kwargs)
        
        sha = Faker(sha)
        sha256 = Faker(sha256)

except:
    import sha as sha1

import settings

class Authorization(object):
    u"""
    Authorization the request
    """
    def __init__(self, sk,  signature):
        u"""
        """
        self.sk = sk
        self.signature = signature
        
        self.get_accesskey_secret()
    

    def create_signature(self):
        u"""
        StringToSign =
        HTTP-Verb + "\n" +
        Content-MD5 + "\n" +
        Content-Type + "\n" +
        Date + "\n" +
        CanonicalizedAmzHeaders +
        CanonicalizedResource;
        see detail http://docs.amazonwebservices.com/AmazonS3/latest/dev/RESTAuthentication.html
        其后面描述有很多复杂的签名,为自定义域名和其他复杂使用而准备的，此处只做简单实现
        """
        headers = headers or self.headers
        accesskey_id = accesskey_id or self.accesskey_id
        url = url or self.url
        url = url.replace('//','/')
        accesskey_secret = accesskey_secret or self.accesskey_secret or 'abcd'  #用于未带签名信息的签名计算
        HTTP_Verb = self.method or headers.get('HTTP-Verb') or headers.get('HTTP-Verb'.upper(),'')
        Content_Type = headers.get('Content-Type') or headers.get('Content-Type'.upper()) or ''
        Content_MD5 = headers.get('Content-MD5') or headers.get('Content-MD5'.upper()) or ''
        Date = headers.get('Date','') or headers.get('Date'.upper(),'')
        CanonicalizedAmzHeaders = ''
        CanonicalizedResource = url
        self.StringToSign = '\n'.join([HTTP_Verb,Content_Type,Content_MD5,Date,CanonicalizedAmzHeaders+CanonicalizedResource])
        #print self.StringToSign
        self.Signature = base64.encodestring(hmac.new(accesskey_secret,self.StringToSign,sha1).digest()).strip()
        #print self.Signature,self.StringToSign
        return self.Signature


    def compare_signature(self, headers=None, Signature=None):
        u"""
        compare two signature
        """
        headers = headers or self.headers
        Signature = Signature or self.Signature
        Authorization = headers.get('Authorization') or headers.get('AUTHORIZATION') or ''
        print 'server Signature >>>',Signature
        print 'get Signature >>>',Authorization.split(':')[-1].strip()
        """
        get的空格会转义++
        server Signature >>> YO++sNdSAwOfJAZkrkrLMTTu3jY=
        get Signature >>> YO  sNdSAwOfJAZkrkrLMTTu3jY=
        server Signature >>> +WFjckq4xJwjW/GozPthYG/WmrM=
        get Signature >>> WFjckq4xJwjW/GozPthYG/WmrM=
        """
        Authorization_get = Authorization.split(':')[-1].rstrip()
        if len(Authorization_get)!=28:
            Authorization_get = Authorization.split(':')[-1][:28] 
        if Authorization_get.replace(' ','+') == Signature or Authorization_get == Signature:
            return True
        else:
            msg = 'The request signature we calculated does not match the signature you provided. Check your key and signing method.'
            _a = AccessDenied(msg,
                    StringToSign=self.StringToSign,
                    AccessKeyID=self.accesskey_id,
                    )        
            return _a.to_django_response()
    

    def checkheader(self,headers=None):
        u"""
        check the http header if include necessary information
        """ 
        headers = headers or self.headers
        list_need_attribute_in_header = [settings.AUTH_HEADER_AUTH.upper()]+[settings.AUTH_META_PREFIX+i for i in settings.AUTH_META]
        
        for i in list_need_attribute_in_header:
            if headers.get(i.upper()) == None :
                msg = 'You Must Need a %s in your Http request header' %i
                _a = MissingSecurityHeader(msg)
                return _a.to_django_response()
        
        return True
        
    def check_date(self,date=None):
        u"""
        Check Date if has expire
        """
        date = date or self.headers.get(settings.AUTH_HEADER_DATE.upper(),)
        try:
            date_time = time.strptime(date,settings.AUTH_HEADER_DATE_FORMATE,)
        except:
            return  InvalidArgument('Your Date Formate Error\n,Date formate:%s' %settings.AUTH_HEADER_DATE_FORMATE).to_django_response()
        
        utime = time.mktime(date_time)
        stime = time.mktime(time.localtime())
        #print utime,stime 
        #print stime-utime ,settings.AUTH_DATE_EXPIRE
        if abs(stime-utime) > settings.AUTH_DATE_EXPIRE:
            return RequestTimeTooSkewed('Your Date Has expire').to_django_response() 

        return True

    def authorization(self):
        u"""
        start authorization a http request if grant
        """
        
        a_ = self.checkheader()
        if not  a_ == True:
            return a_
        
        b_ = self.check_date()
        if not b_ == True:
            return b_


        if not self.get_accesskey_id():
            return InvalidAccessKeyId().to_django_response()
        
        if not self.get_accesskey_secret():
            return InvalidAccessKeyId().to_django_response()
        
        self.create_signature()
        rst = self.compare_signature()
        return rst


    def granted(self):
        self.create_signature()
        rst = self.compare_signature()
        if not rst == True:
            return False
        else:
            return True

