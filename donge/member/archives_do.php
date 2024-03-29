<?php
require_once(dirname(__FILE__)."/config.php");
if(empty($dopost))
{
	$dopost = '';
}
$aid = isset($aid) && is_numeric($aid) ? $aid : 0;
$channelid = isset($channelid) && is_numeric($channelid) ? $channelid : 1;

/*-----------------
function delStow()
删除收藏
------------------*/
if($dopost=="delStow")
{
	CheckRank(0,0);
	$ENV_GOBACK_URL = empty($_COOKIE['ENV_GOBACK_URL']) ? "mystow.php" : $_COOKIE['ENV_GOBACK_URL'];
	$dsql->ExecuteNoneQuery("Delete From #@__member_stow where aid='$aid' And mid='".$cfg_ml->M_ID."'; ");
	//更新用户统计
	$row = $dsql->GetOne("SELECT COUNT(*) AS nums FROM `#@__member_stow` WHERE `mid`='".$cfg_ml->M_ID."' ");
	$dsql->ExecuteNoneQuery("UPDATE #@__member_tj SET `stow`='$row[nums]' WHERE `mid`='".$cfg_ml->M_ID."'");
		
	ShowMsg("成功删除一条收藏记录！",$ENV_GOBACK_URL);
	exit();
}

/*-----------------
function addArchives()
添加投稿
------------------*/
else if($dopost=="addArc")
{
	if($channelid==1)
	{
		$addcon = 'article_add.php?channelid='.$channelid;
	}
	else if($channelid==2)
	{
		$addcon = 'album_add.php?channelid='.$channelid;
	}
	else if($channelid==3)
	{
		$addcon = 'soft_add.php?channelid='.$channelid;
	}
	else
	{
		$row = $dsql->GetOne("Select useraddcon From `#@__channeltype` where id='$channelid' ");
		if(!is_array($row))
		{
			ShowMsg("模型参数错误!","-1");
			exit();
		}
		$addcon = $row['useraddcon'];
		if(trim($addcon)=='')
		{
			$addcon = 'archives_add.php';
		}
		$addcon = $addcon."?channelid=$channelid";
	}
	header("Location:$addcon");
	exit();
}

/*-----------------
function editArchives()
修改投稿
------------------*/
else if($dopost=="edit")
{
	CheckRank(0,0);
	if($channelid==1)
	{
		$edit = 'article_edit.php?channelid='.$channelid;
	}
	else if($channelid==2)
	{
		$edit = 'album_edit.php?channelid='.$channelid;
	}
	else if($channelid==3)
	{
		$edit = 'soft_edit.php?channelid='.$channelid;
	}
	else
	{
		$row = $dsql->GetOne("Select usereditcon From `#@__channeltype` where id='$channelid' ");
		if(!is_array($row))
		{
			ShowMsg("参数错误!","-1");
			exit();
		}
		$edit = $row['usereditcon'];
		if(trim($edit)=='')
		{
			$edit = 'archives_edit.php';
		}
		$edit = $edit."?channelid=$channelid";
	}
	header("Location:$edit"."&aid=$aid");
	exit();
}

/*--------------------
function delArchives()
删除文章
--------------------*/
else if($dopost=="delArc")
{
	CheckRank(0,0);
	include_once(DEDEMEMBER."/inc/inc_batchup.php");
	$ENV_GOBACK_URL = empty($_COOKIE['ENV_GOBACK_URL']) ? 'content_list.php?channelid=' : $_COOKIE['ENV_GOBACK_URL'];


	$equery = "Select arc.channel,arc.senddate,arc.arcrank,ch.maintable,ch.addtable,ch.issystem,ch.arcsta From `#@__arctiny` arc
	           left join `#@__channeltype` ch on ch.id=arc.channel where arc.id='$aid' ";

	$row = $dsql->GetOne($equery);
	if(!is_array($row))
	{
		ShowMsg("你没有权限删除这篇文档！","-1");
		exit();
	}
	if(trim($row['maintable'])=='') $row['maintable'] = '#@__archives';
	if($row['issystem']==-1)
	{
		$equery = "Select mid from `{$row['addtable']}` where aid='$aid' And mid='".$cfg_ml->M_ID."' ";
	}
	else
	{
		$equery = "Select mid,litpic from `{$row['maintable']}` where id='$aid' And mid='".$cfg_ml->M_ID."' ";
	}
	$arr = $dsql->GetOne($equery);
	if(!is_array($arr))
	{
		ShowMsg("你没有权限删除这篇文档！","-1");
		exit();
	}

	if($row['arcrank']>=0)
	{
		$dtime = time();
		$maxtime = $cfg_mb_editday * 24 *3600;
		if($dtime - $row['senddate'] > $maxtime)
		{
			ShowMsg("这篇文档已经锁定，你不能再删除它！","-1");
			exit();
		}
	}

	$channelid = $row['channel'];
	$row['litpic'] = (isset($arr['litpic']) ? $arr['litpic'] : '');

	//删除文档
	if($row['issystem']!=-1) $rs = DelArc($aid);
	else $rs = DelArcSg($aid);

	//删除缩略图
	if(trim($row['litpic'])!='' && ereg("^".$cfg_user_dir."/{$cfg_ml->M_ID}",$row['litpic']))
	{
		$dsql->ExecuteNoneQuery("Delete From `#@__uploads` where url like '{$row['litpic']}' And mid='{$cfg_ml->M_ID}' ");
		@unlink($cfg_basedir.$row['litpic']);
	}

	if($ENV_GOBACK_URL=='content_list.php?channelid=')
	{
		$ENV_GOBACK_URL = $ENV_GOBACK_URL.$channelid;
	}
	if($rs)
	{
		//更新用户记录
		countArchives($channelid);
		//扣除积分
		$dsql->ExecuteNoneQuery("Update `#@__member` set scores=scores-{$cfg_sendarc_scores} where mid='".$cfg_ml->M_ID."' And (scores-{$cfg_sendarc_scores}) > 0; ");
		ShowMsg("成功删除一篇文档！",$ENV_GOBACK_URL);
		exit();
	}
	else
	{
		ShowMsg("删除文档失败！",$ENV_GOBACK_URL);
	  exit();
	}
	exit();
}

/*-----------------
function viewArchives()
查看文章
------------------*/
else if($dopost=="viewArchives")
{
	CheckRank(0,0);
	header("location:".$cfg_phpurl."/view.php?aid=".$aid);
}

/*--------------
function DelUploads()
删除上传的附件
----------------*/
else if($dopost=="delUploads")
{
	CheckRank(0,0);
	if(empty($ids))
	{
		$ids = '';
	}

	$tj = 0;
	if($ids=='')
	{
		$arow = $dsql->GetOne("Select url,mid From `#@__uploads` where aid='$aid'; ");
		if(is_array($arow) && $arow['mid']==$cfg_ml->M_ID)
		{
			$dsql->ExecuteNoneQuery("Delete From `#@__uploads` where aid='$aid'; ");
			if(file_exists($cfg_basedir.$arow['url']))
			{
				@unlink($cfg_basedir.$arow['url']);
			}
		}
		$tj++;
	}
	else
	{
		$ids = explode(',',$ids);
		foreach($ids as $aid)
		{
			$aid = ereg_replace("[^0-9]","",$aid);
			$arow = $dsql->GetOne("Select url,mid From #@__uploads where aid='$aid'; ");
			if(is_array($arow) && $arow['mid']==$cfg_ml->M_ID)
			{
				$dsql->ExecuteNoneQuery("Delete From `#@__uploads` where aid='$aid'; ");
				$tj++;
				if(file_exists($cfg_basedir.$arow['url']))
				{
					@unlink($cfg_basedir.$arow['url']);
				}
			}
		}
	}
	ShowMsg("成功删除 $tj 个附件！",$ENV_GOBACK_URL);
	exit();
}

?>