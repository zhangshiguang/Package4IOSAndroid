#!/usr/bin/env ruby
# 脚本编译前，检查项目的所有依赖项目都加到配置中；===>否则，脚本 -target Order 编译出错；
# 越狱包 签名都是 developer 签名；
# 编译 three2.0时头文件找不到的问题，在源代码中修改 头文件引用语句：删除 “/private” ；
# 经测试发现 xcrun 打包不会把 iTunesArtwork 图片文件答进ipa包中；故使用zip 打包。 
###########################
#在项目中配置好 -sdk版本，命令行业可以指定 。
		#xcodebuild -showsdks
		#-sdk iphoneos7.1
#Three20Core 的
#searth path 配置："$(BUILD_DIR)/Products/three20/"  ===》经测试，不起作用，在编译Three20Core时 BUILD_DIR 的路径需要弄清楚。
#
#
########################################################################

require "rubygems" 
gem 'rubyzip'  
require 'zip'

require 'FileUtils'
require 'date'
require 'find'

$projectname={your project name}
$N = '\n'
$Rn ='\r\n'
$channelList = [] 
$chf ='./channel'
$cppfile ="./#($projectname)/Classes/ISSConnect.m
$cppfile_al ="./#($projectname)/Classes/ISSConnect2.m"

$appBuild ='./build/Release-iphoneos/Order.app'
$appDesktop ="~/Desktop/Payload/app/Payload/#($projectname).app"
$ipapath  ='/~/Desktop/Payload/bin/' 


#准备好目录
#FileUtils.mkpath('~/Desktop/Payload/app/Payload/')  unless File.exist?('~/Desktop/Payload/app/Payload/')
#exit


######################################################################

class Zipper
 
  def self.zip(dir, zip_dir, remove_after = false)
    Zip::ZipFile.open(zip_dir, Zip::ZipFile::CREATE)do |zipfile|
      Find.find(dir) do |path|
        Find.prune if File.basename(path)[0] == ?.
        dest = /#{dir}\/(\w.*)/.match(path)
        # Skip files if they exists
        begin
          zipfile.add(dest[1],path) if dest
        rescue Zip::ZipEntryExistsError
        end
      end
    end
    FileUtils.rm_rf(dir) if remove_after
  end
 
#
#We catch Zip::ZipEntryExistsError exception – so we won’t overwrite files in an archive if the file already exist. After all (no exceptions raised) we can remove the source directory:
#Zipper.zip('/home/user/directory', '/home/user/compressed.zip')
#

###
 
  def self.unzip(zip, unzip_dir, remove_after = false)
    Zip::ZipFile.open(zip) do |zip_file|
      zip_file.each do |f|
        f_path=File.join(unzip_dir, f.name)
        FileUtils.mkdir_p(File.dirname(f_path))
        zip_file.extract(f, f_path) unless File.exist?(f_path)
      end
    end
    FileUtils.rm(zip) if remove_after
  end
 

#
#Usage is similar to the zip method. We provide zip file, directory to unzip and we decide whether or not to remove source file after unzipping its content.
#Zipper.unzip('/home/user/compressed.zip','/home/user/directory', true)
#


 
  def self.open_one(zip_source, file_name)
    Zip::ZipFile.open(zip_source) do |zip_file|
      zip_file.each do |f|
        next unless "#{f}" == file_name
        return f.get_input_stream.read
      end
    end
    nil
  end
 
end

#
#Usage:
#Zipper.open_one('/home/user/source.zip','subdir_in_zip/file.ext')
#
###################################################################

def getchannel	
	if File.exist?($chf)
	   File.open($chf,'r') do |f|
	       f.each_line do |line|  #while line=f.gets
             if line.match(',')
                $channelList.push(line.strip())
                #puts ' ', line
             end
	       end      
	    end
	else
	  puts "File #{$chf} was not found"
	  exit
	end
end

def replacech(channel)
  
  File.open($cppfile_al,'w') do | fn |
    File.open($cppfile,'r') do |fi| 
        fi.each_line do | line |
          puts line
          if line.match(/ch=[\d+]/)                       ## &ch=00000000
             line.gsub!(Regexp.new('ch=\d*' ),channel)
          end
          fn.puts line       
          puts line
        end    
    end
  end  
  File.delete($cppfile)
  File.rename($cppfile_al,$cppfile)
end        

#####################################

def main
	 
   
	$channelList.each do |a| 
	
	  chValue,chName = a.split(",") 
	  puts '渠道号码：' , chValue  
	  puts '渠道 ： ', chName

	  replacech chValue
	  
	  if !system('xcodebuild -target Order -configuration Release clean')
	     puts 'clean error' 
	     exit
	  end
	  
		if !system('xcodebuild -target Order -configuration Release CODE_SIGN_IDENTITY="iPhone Developer: ZuXiong Liu (743KN38XB2)"')
	     puts 'xcodebuild error' 
	     exit
	  end

	  #build 完成后生成在这里#./{your project dir}/build/Release-iphoneos/{your project name}.app
	  
	  FileUtils.rm_rf $appDesktop  
	  FileUtils.cp_r $appBuild  , $appDesktop
	  
	  #
	  d = DateTime.now
	  chName += '_' + d.year.to_s + '_'+ d.month.to_s + '_' + d.day.to_s
	  ipafile = "#{$ipapath}aiya_#{chName}.ipa"
	  
	  Zipper.zip('/Users/apple/Desktop/Payload/app/*', ipafile)
	  
	  #发布到服务器
	 
	  #FileUtils.cp ipafile ,'~/projects/.'
	  
	end
end


#
#if !system("mount_smbfs -f777 -d777 //server:pwd@192.168.1.183/ShareFolder/Release/ios  ~/projects")
  #映射成功后，可以直接复制到  ~/projects	，就复制到服务器上了
#end


#
#
#
#
#

getchannel

main
