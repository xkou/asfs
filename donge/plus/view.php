<?php

/**
 *
 * 关于文章权限设置的说明
 * 文章权限设置限制形式如下：
 * 如果指定了会员等级，那么必须到达这个等级才能浏览
 * 如果指定了金币，浏览时会扣指点的点数，并保存记录到用户业务记录中
 * 如果两者同时指定，那么必须同时满足两个条件
 *
 */

require_once(dirname(__FILE__)."/../include/common.inc.php");
require_once(DEDEINC.'/arc.archives.class.php');

$t1 = ExecTime();

if(empty($okview))
{
	$okview = '';
}

if(isset($arcID))
{
	$aid = $arcID;
}

$arcID = $aid = (isset($aid) && is_numeric($aid)) ? $aid : 0;
if($aid==0)
{
	die(" Request Error! ");
}

$arc = new Archives($aid);
if($arc->IsError)
{
	ParamError();
}

//检查阅读权限
$needMoney = $arc->Fields['money'];
$needRank = $arc->Fields['arcrank'];

//设置了权限限制的文章
//arctitle msgtitle moremsg
if($needMoney>0 || $needRank>1)
{
	require_once(DEDEINC.'/memberlogin.class.php');
	$cfg_ml = new MemberLogin();
	$arctitle = $arc->Fields['title'];
	/*
	$arclink = GetFileUrl($arc->ArcID,$arc->Fields["typeid"],$arc->Fields["senddate"],
	                         $arc->Fields["title"],$arc->Fields["ismake"],$arc->Fields["arcrank"]);
	*/                        
	$arclink = $cfg_phpurl.'/view.php?aid='.$arc->ArcID;                         
	$arcLinktitle = "<a href=\"{$arclink}\"><u>".$arctitle."</u></a>";
	
	$description =  $arc->Fields["description"];
	$pubdate = GetDateTimeMk($arc->Fields["pubdate"]);
	
	//会员级别不足
	if(($needRank>1 && $cfg_ml->M_Rank < $needRank && $arc->Fields['mid']!=$cfg_ml->M_ID))
	{
		$dsql->Execute('me' , "Select * From `#@__arcrank` ");
		while($row = $dsql->GetObject('me'))
		{
			$memberTypes[$row->rank] = $row->membername;
		}
		$memberTypes[0] = "游客或没权限会员";
		$msgtitle = "你没有权限浏览文档：{$arctitle} ！";
		$moremsg = "这篇文档需要 <font color='red'>".$memberTypes[$needRank]."</font> 才能访问，你目前是：<font color='red'>".$memberTypes[$cfg_ml->M_Rank]."</font> ！";
		include_once(DEDETEMPLATE.'/plus/view_msg.htm');
		exit();
	}

	//需要金币的情况
	if( $needMoney > 0  && $arc->Fields['mid'] != $cfg_ml->M_ID)
	{
		$sql = "Select aid,money From `#@__member_operation` where buyid='ARCHIVE".$aid."' And mid='".$cfg_ml->M_ID."'";
		$row = $dsql->GetOne($sql);
		//未购买过此文章
		if(!is_array($row))
		{
			if( $cfg_ml->M_Money=='' || $needMoney > $cfg_ml->M_Money)
	 		{
					$msgtitle = "你没有权限浏览文档：{$arctitle} ！";
					$moremsg = "这篇文档需要 <font color='red'>".$needMoney." 金币</font> 才能访问，你目前拥有金币：<font color='red'>".$cfg_ml->M_Money." 个</font> ！";
					include_once(DEDETEMPLATE.'/plus/view_msg.htm');
					$arc->Close();
					exit();
			}
			else
			{
					$inquery = "INSERT INTO `#@__member_operation`(mid,oldinfo,money,mtime,buyid,product,pname,sta)
		              VALUES ('".$cfg_ml->M_ID."','$arctitle','$needMoney','".time()."', 'ARCHIVE".$aid."', 'archive','购买文章', 2); ";
		 	 		if(!$dsql->ExecuteNoneQuery($inquery))
		 	 		{
							ShowMsg('保存购买记录失败， 请与管理员联系！', '-1');
							exit;
					}
					$dsql->ExecuteNoneQuery("Update `#@__member` set money=money-$needMoney where mid='".$cfg_ml->M_ID."'");
			}
		}
	}//金币处理付处理
	
}
$arc->Display();

?>