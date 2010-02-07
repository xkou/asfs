<?php
require_once(dirname(__FILE__)."/config.php");
if(empty($uid))
{
	$uid = '';
}
if(empty($action))
{
	$action = '';
}

//会员后台
if($uid=='')
{
	$iscontrol = 'yes';
	if(!$cfg_ml->IsLogin())
	{
		header('Location: /member/login.php?gourl=/member/');
		exit(0);
		include_once(dirname(__FILE__)."/templets/index-notlogin.htm");
	}
	else
	{
		$minfos = $dsql->GetOne("Select * From `#@__member_tj` where mid='".$cfg_ml->M_ID."'; ");
		$minfos['totaluse'] = $cfg_ml->GetUserSpace();
		$minfos['totaluse'] = number_format($minfos['totaluse']/1024/1024,2);
		if($cfg_mb_max>0)
		{
			$ddsize = ceil( ($minfos['totaluse']/$cfg_mb_max) * 100 );
		}
		else
		{
			$ddsize = 0;
		}

		require_once(DEDEINC.'/channelunit.func.php');

		
		$dpl = new DedeTemplate();
		$tpl = dirname(__FILE__)."/templets/index.htm";
		$dpl->LoadTemplate($tpl);
		$dpl->display();
	}
}

/*-----------------------------
//会员空间主页
function space_index(){  }
------------------------------*/
else
{
	require_once(DEDEMEMBER."/inc/config_space.php");
	if($action == '')
	{
		include_once(DEDEINC."/channelunit.func.php");
		$dpl = new DedeTemplate();
		$tplfile = DEDEMEMBER."/space/{$_vars['spacestyle']}/index.htm";

		//更新最近访客记录及站点统计记录
		$vtime = time();
		$last_vtime = GetCookie('last_vtime');
		$last_vid = GetCookie('last_vid');
		if(empty($last_vtime))
		{
			$last_vtime = 0;
		}
		if($vtime - $last_vtime > 3600 || !eregi(','.$uid.',',','.$last_vid.',') )
		{
			if($last_vid!='')
			{
				$last_vids = explode(',',$last_vid);
				$i = 0;
				$last_vid = $uid;
				foreach($last_vids as $lsid)
				{
					if($i>10)
					{
						break;
					}
					else if($lsid != $uid)
					{
						$i++;
						$last_vid .= ','.$last_vid;
					}
				}
			}
			else
			{
				$last_vid = $uid;
			}
			PutCookie('last_vtime',$vtime,3600*24,"/");
			PutCookie('last_vid',$last_vid,3600*24,"/");
			if($cfg_ml->IsLogin() && $cfg_ml->M_LoginID!=$uid)
			{
				$vip = GetIP();
				$arr = $dsql->GetOne("Select * From `#@__member_vhistory` where mid='{$_vars['mid']}' And vid='{$cfg_ml->M_ID}' ");
				if(is_array($arr))
				{
					$dsql->ExecuteNoneQuery("Update `#@__member_vhistory` set vip='$vip',vtime='$vtime',count=count+1 where mid='{$_vars['mid']}' And vid='{$cfg_ml->M_ID}' ");
				}
				else
				{
					$query = "Insert Into `#@__member_vhistory`(mid,loginid,vid,vloginid,count,vip,vtime)
		 	  	          Values('{$_vars['mid']}','{$_vars['userid']}','{$cfg_ml->M_ID}','{$cfg_ml->M_LoginID}','1','$vip','$vtime'); ";
					$dsql->ExecuteNoneQuery($query);
				}
			}
			$dsql->ExecuteNoneQuery("Update `#@__member_tj` set homecount=homecount+1 where mid='{$_vars['mid']}' ");
		}
		$dpl->LoadTemplate($tplfile);
		$dpl->display();
	}
	else
	{
		require_once(DEDEMEMBER."/inc/space_action.php");
	}
}

?>