<?php
require_once(dirname(__FILE__)."/config.php");
require_once(DEDEINC."/oxwindow.class.php");
if(empty($dopost))
{
	$dopost = '';
}
if(empty($fmdo))
{
	$fmdo = '';
}
$ENV_GOBACK_URL = isset($_COOKIE['ENV_GOBACK_URL']) ? 'member_main.php' : '';

/*----------------
function __DelMember()
删除会员
----------------*/
if($dopost=="delmember")
{
	CheckPurview('member_Del');
	if($fmdo=='yes')
	{
		$id = ereg_replace('[^0-9]','',$id);
		$safecodeok = substr(md5($cfg_cookie_encode.$randcode),0,24);
		if($safecodeok!=$safecode)
		{
			ShowMsg("请填写正确的安全验证串！","member_do.php?id={$id}&dopost=delmember");
			exit();
		}
		if(!empty($id))
		{
			//删除用户信息
			$row = $dsql->GetOne("Select * From `#@__member` where mid='$id' limit 1 ");
			$rs = 0;
			if($row['matt'] == 10)
			{
				$nrow = $dsql->GetOne("Select * From `#@__admin` where id='$id' limit 1 ");
				//已经删除关连的管理员帐号
				if(!is_array($nrow)) $rs = $dsql->ExecuteNoneQuery2("Delete From `#@__member` where mid='$id' limit 1");
			}
			else
			{
				$rs = $dsql->ExecuteNoneQuery2("Delete From `#@__member` where mid='$id' limit 1");
			}
			if($rs > 0)
			{
				$dsql->ExecuteNoneQuery("Delete From `#@__member_tj` where mid='$id' limit 1");
				$dsql->ExecuteNoneQuery("Delete From `#@__member_space` where mid='$id' limit 1");
				$dsql->ExecuteNoneQuery("Delete From `#@__member_company` where mid='$id' limit 1");
				$dsql->ExecuteNoneQuery("Delete From `#@__member_person` where mid='$id' limit 1");

				//删除用户相关数据
				$dsql->ExecuteNoneQuery("Delete From `#@__member_stow` where mid='$id' ");
				$dsql->ExecuteNoneQuery("Delete From `#@__member_flink` where mid='$id' ");
				$dsql->ExecuteNoneQuery("Delete From `#@__member_guestbook` where mid='$id' ");
				$dsql->ExecuteNoneQuery("Delete From `#@__member_operation` where mid='$id' ");
				$dsql->ExecuteNoneQuery("Delete From `#@__member_pms` where toid='$id' Or fromid='$id' ");
				$dsql->ExecuteNoneQuery("Delete From `#@__member_friends` where mid='$id' Or fid='$id' ");
				$dsql->ExecuteNoneQuery("Delete From `#@__member_vhistory` where mid='$id' Or vid='$id' ");
				$dsql->ExecuteNoneQuery("Delete From `#@__feedback` where mid='$id' ");
				$dsql->ExecuteNoneQuery("update `#@__archives` set mid='0' where mid='$id'");
				#api{{
				if(defined('UC_API') && @include_once DEDEROOT.'/uc_client/client.php')	uc_user_delete($row['userid']);
				#/aip}}
			}
			else
			{
				ShowMsg("无法删除此会员，如果这个会员是<b>[管理员]</b>，<br />必须先删除这个<b>[管理员]</b>才能删除此帐号！", $ENV_GOBACK_URL, 0, 5000);
				exit();
			}
		}
		ShowMsg("成功删除一个会员！",$ENV_GOBACK_URL);
		exit();
	}
	$randcode = mt_rand(10000,99999);
	$safecode = substr(md5($cfg_cookie_encode.$randcode),0,24);
	$wintitle = "会员管理-删除会员";
	$wecome_info = "<a href='".$ENV_GOBACK_URL."'>会员管理</a>::删除会员";
	$win = new OxWindow();
	$win->Init("member_do.php","js/blank.js","POST");
	$win->AddHidden("fmdo","yes");
	$win->AddHidden("dopost",$dopost);
	$win->AddHidden("id",$id);
	$win->AddHidden("randcode",$randcode);
	$win->AddHidden("safecode",$safecode);
	$win->AddTitle("你确实要删除(ID:".$id.")这个会员?");
	$win->AddMsgItem("安全验证串：<input name='safecode' type='text' id='safecode' size='16' style='width:200px' />&nbsp;(复制本代码： <font color='red'>$safecode</font> )","30");
	$winform = $win->GetWindow("ok");
	$win->Display();
}
/*----------------
function __Recommend()
推荐会员
----------------*/
else if($dopost=="recommend")
{
	CheckPurview('member_Edit');
	$id = ereg_replace("[^0-9]","",$id);
	if($matt==0)
	{
		$dsql->ExecuteNoneQuery("update `#@__member` set matt=1 where mid='$id' And matt<>10 limit 1");
		ShowMsg("成功设置一个会员推荐！",$ENV_GOBACK_URL);
		exit();
	}
	else
	{
		$dsql->ExecuteNoneQuery("update `#@__member` set matt=0 where mid='$id' And matt<>10 limit 1");
		ShowMsg("成功取消一个会员推荐！",$ENV_GOBACK_URL);
		exit();
	}
}
/*----------------
function __EditUser()
更改会员
----------------*/
else if($dopost=='edituser')
{
	CheckPurview('member_Edit');
	if(!isset($_POST['id'])) exit('Request Error!');
	$pwdsql = empty($pwd) ? '' : ",pwd='".md5($pwd)."'";
	if(empty($sex)) $sex = '男';
	
	if($matt==10 && $oldmatt!=10)
	{
		ShowMsg("对不起，为安全起见，不支持直接把前台会员转为管理的操作！", "-1");
		exit();
	}	
	$query = "update `#@__member` set
			email = '$email',
			uname = '$uname',
			sex = '$sex',
			matt = '$matt',
			money = '$money',
			scores = '$scores',
			rank = '$rank',
			spacesta='$spacesta'
			$pwdsql
			where mid='$id' And matt<>10 ";
	$rs = $dsql->ExecuteNoneQuery2($query);
	if($rs==0)
	{
		$query = "update `#@__member` set
			email = '$email',
			uname = '$uname',
			sex = '$sex',
			money = '$money',
			scores = '$scores',
			rank = '$rank',
			spacesta='$spacesta'
			$pwdsql
			where mid='$id' ";
			$rs = $dsql->ExecuteNoneQuery2($query);
	}
	
	#api{{
	if(defined('UC_API') && @include_once DEDEROOT.'/api/uc.func.php')
	{
		$row = $dsql->GetOne("SELECT `scores`,`userid` FROM `#@__member` WHERE `mid`='$id' AND `matt`<>10");
		$amount = $scores-$row['scores'];
		uc_credit_note($row['userid'],$amount);
	}
	#/aip}}
	
	ShowMsg('成功更改会员资料！', 'member_view.php?id='.$id);
	exit();
}
/*--------------
function __LoginCP()
登录会员的控制面板
----------*/
else if($dopost=="memberlogin")
{
	CheckPurview('member_Edit');
	PutCookie('DedeUserID',$id,1800);
	PutCookie('DedeLoginTime',time(),1800);
	if(empty($jumpurl)) header("location:../member/index.php");
	else header("location:$jumpurl");
}
elseif($dopost == "upoperations")
{
	$nid = ereg_replace('[^0-9,]','',ereg_replace('`',',',$nid));
	$nid = explode(',',$nid);
	if(is_array($nid))
	{
		foreach ($nid as $var)
		{
			$query = "update `#@__member_operation` set sta = '1' where aid = '$var'";
			$dsql->ExecuteNoneQuery($query);
			ShowMsg("设置成功！","member_operations.php");
			exit();
		}
	}
}
elseif($dopost == "okoperations")
{
	$nid = ereg_replace('[^0-9,]','',ereg_replace('`',',',$nid));
	$nid = explode(',',$nid);
	if(is_array($nid))
	{
		foreach ($nid as $var)
		{
			$query = "update `#@__member_operation` set sta = '2' where aid = '$var'";
			$dsql->ExecuteNoneQuery($query);
			ShowMsg("设置成功！","member_operations.php");
			exit();
		}
	}
}
?>