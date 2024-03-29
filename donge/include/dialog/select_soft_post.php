<?php
if(!isset($cfg_basedir))
{
	include_once(dirname(__FILE__).'/config.php');
}
if(empty($uploadfile)) $uploadfile = '';
if(empty($uploadmbtype)) $uploadmbtype = '软件类型';
if(empty($bkurl)) $bkurl = 'select_soft.php';
$newname = ( empty($newname) ? '' : ereg_replace("[\\ \"\*\?\t\r\n<>':/|]", "", $newname) );

if(!is_uploaded_file($uploadfile))
{
	ShowMsg("你没有选择上传的文件或选择的文件大小超出限制!", "-1");
	exit();
}

//软件类型为所有支持的附件
$cfg_softtype = $cfg_softtype.'|'.$cfg_imgtype.'|'.$cfg_mediatype;
$cfg_softtype = str_replace('||', '|', $cfg_softtype);
$uploadfile_name = trim(ereg_replace("[ \r\n\t\*\%\\/\?><\|\":]{1,}",'',$uploadfile_name));
if(!eregi("\.(".$cfg_softtype.")", $uploadfile_name))
{
	ShowMsg("你所上传的{$uploadmbtype}不在许可列表，请更改系统对扩展名限定的配置！","-1");
	exit();
}

$nowtme = time();
if($activepath==$cfg_soft_dir)
{
	$newdir = MyDate($cfg_addon_savetype, $nowtme);
	$activepath = $activepath.'/'.$newdir;
	if(!is_dir($cfg_basedir.$activepath))
	{
		MkdirAll($cfg_basedir.$activepath,$cfg_dir_purview);
		CloseFtp();
	}
}

//文件名（前为手工指定， 后者自动处理）
if(!empty($newname))
{
	$filename = $newname;
	if(!ereg("\.", $filename)) $fs = explode('.', $uploadfile_name);
	else $fs = explode('.', $filename);
	if(eregi($cfg_not_allowall, $fs[count($fs)-1]))
	{
		ShowMsg("你指定的文件名被系统禁止！",'javascript:;');
		exit();
	}
	if(!ereg("\.", $filename)) $filename = $filename.'.'.$fs[count($fs)-1];
}
else
{
	$filename = $cuserLogin->getUserID().'-'.dd2char(MyDate('ymdHis',$nowtme));
	$fs = explode('.', $uploadfile_name);
	if(eregi($cfg_not_allowall, $fs[count($fs)-1]))
	{
		ShowMsg("你上传了某些可能存在不安全因素的文件，系统拒绝操作！",'javascript:;');
		exit();
	}
	$filename = $filename.'.'.$fs[count($fs)-1];
}

$fullfilename = $cfg_basedir.$activepath.'/'.$filename;
$fullfileurl = $activepath.'/'.$filename;
move_uploaded_file($uploadfile,$fullfilename) or die("上传文件到 $fullfilename 失败！");
@unlink($uploadfile);

if($uploadfile_type == 'application/x-shockwave-flash')
{
	$mediatype=2;
}
else if(eregi('image',$uploadfile_type))
{
	$mediatype=1;
}
else if(eregi('audio|media|video',$uploadfile_type))
{
	$mediatype=3;
}
else
{
	$mediatype=4;
}

$inquery = "INSERT INTO `#@__uploads`(arcid,title,url,mediatype,width,height,playtime,filesize,uptime,mid)
   VALUES ('0','$filename','$fullfileurl','$mediatype','0','0','0','{$uploadfile_size}','{$nowtme}','".$cuserLogin->getUserID()."'); ";

$dsql->ExecuteNoneQuery($inquery);
$fid = $dsql->GetLastID();
AddMyAddon($fid, $fullfileurl);

ShowMsg("成功上传文件！",$bkurl."?comeback=".urlencode($filename)."&f=$f&activepath=".urlencode($activepath)."&d=".time());
exit();
?>