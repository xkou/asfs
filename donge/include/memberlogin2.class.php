<?php
if(!defined('DEDEINC'))
{
	exit("Request Error!");
}

//检查用户名的合法性
function CheckUserID($uid,$msgtitle='用户名',$ckhas=true)
{
	global $cfg_mb_notallow,$cfg_mb_idmin,$cfg_md_idurl,$cfg_soft_lang,$dsql;
	if($cfg_mb_notallow != '')
	{
		$nas = explode(',',$cfg_mb_notallow);
		if(in_array($uid,$nas))
		{
			return $msgtitle.'为系统禁止的标识！';
		}
	}
	if($cfg_md_idurl=='Y' && eregi("[^a-z0-9]",$uid))
	{
		return $msgtitle.'必须由英文字母或数字组成！';
	}

	if($cfg_soft_lang=='utf-8')
	{
		$ck_uid = utf82gb($uid);
	}
	else
	{
		$ck_uid = $uid;
	}

	for($i=0;isset($ck_uid[$i]);$i++)
	{
			if(ord($ck_uid[$i]) > 0x80)
			{
				if(isset($ck_uid[$i+1]) && ord($ck_uid[$i+1])>0x40)
				{
					$i++;
				}
				else
				{
					return $msgtitle.'可能含有乱码，建议你改用英文字母和数字组合！';
				}
			}
			else
			{
				if(eregi("[^0-9a-z@\.-]",$ck_uid[$i]))
				{
					return $msgtitle.'不能含有 [@]、[.]、[-]以外的特殊符号！';
				}
			}
	}
	if($ckhas)
	{
		$row = $dsql->GetOne("Select * From `#@__member` where userid like '$uid' ");
		if(is_array($row)) return $msgtitle."已经存在！";
	}
	return 'ok';
}

//保存一则消息记录
function PutSnsMsg($mid, $userid, $msg)
{
	global $dsql;
	$msg = addslashes($msg);
	$query = "Insert Into `#@__member_snsmsg`(`mid`, `userid`, `sendtime`, `msg`) Values('$mid', '$userid', '".time()."', '$msg'); ";
	$rs = $dsql->ExecuteNoneQuery($query);
	return $rs;
}

//检查用户是否被禁言
function CheckNotAllow()
{
	global $dsql, $cfg_ml, $cfg_mb_spacesta;
	if(empty($cfg_ml->M_ID)) return ;
	if($cfg_ml->M_Spacesta == -2)
	{
		ShowMsg("你已经被禁言，请与管理员联系！", "-1");
		exit();
	}
	else if($cfg_ml->M_Spacesta < 0)
	{
		ShowMsg('系统开启了审核机制，因此你的帐号需要管理员审核后才能发信息！', '-1');
		exit();
	}
}


//网站会员登录类
class MemberLogin
{
	var $M_ID;
	var $M_LoginID;
	var $M_SpaceID;
	var $M_MbType;
	var $M_Uprank;
	var $M_Money;
	var $M_Scores;
	var $M_UserName;
	var $M_Rank;
	var $M_LoginTime;
	var $M_KeepTime;
	var $M_Upmoney;
	var $M_Spacesta;
	var $fields;
	var $isAdmin;

	var $M_Honor = '';

	//php5构造函数
	function __construct($kptime = -1)
	{
		global $dsql;
		if($kptime==-1)
		{
			$this->M_KeepTime = 3600 * 24 * 7;
		}
		else
		{
			$this->M_KeepTime = $kptime;
		}
		$this->M_ID = $this->GetNum(GetCookie("DedeUserID"));
		$this->M_LoginTime = GetCookie("DedeLoginTime");
		$this->fields = array();
		$this->isAdmin = false;
		if(empty($this->M_ID))
		{
			$this->ResetUser();
		}
		else
		{
			$this->M_ID = intval($this->M_ID);
			$this->fields = $dsql->GetOne("Select * From `#@__member` where mid='{$this->M_ID}' ");
			if(is_array($this->fields))
			{
				#api{{
				if(defined('UC_APPID'))
				{
					include_once DEDEROOT.'/uc_client/client.php';
					if($data = uc_get_user($this->fields['userid']))
					{
						list($uid, $username, $email) = $data;
						if(uc_check_avatar($uid) && !strstr($this->fields['face'],UC_API))
						{
							$face = UC_API.'/avatar.php?uid='.$uid.'&size=middle';
							$dsql->ExecuteNoneQuery("UPDATE `#@__member` SET `face`='$face' WHERE `mid`='{$this->M_ID}'");
						}
					}
				}
				#/aip}}
				//间隔一小时更新一次用户登录时间
				if(time() - $this->M_LoginTime > 3600)
				{
					$dsql->ExecuteNoneQuery("update `#@__member` set logintime='".time()."',loginip='".GetIP()."' where mid='".$this->fields['mid']."';");
					PutCookie("DedeLoginTime",time(),$this->M_KeepTime);
				}
				$this->M_LoginID = $this->fields['userid'];
				$this->M_SpaceID = 0;
				$this->M_MbType = $this->fields['mtype'];
				$this->M_Uprank = $this->fields['uprank'];
				$this->M_Money = $this->fields['money'];
				$this->M_Gold	= 0;
				$this->M_MsgNumber	= 0;
				$this->M_UserName = $this->fields['uname'];
				$this->M_Upmoney = $this->fields['upmoney'];
				$this->M_Scores = $this->fields['scores'];
				$this->M_Rank = $this->fields['rank'];
				$this->M_Spacesta = $this->fields['spacesta'];
				$this->M_JoinTime = $this->fields['jointime'];
				$sql = "select uid from uchome_space where username='".$this->M_LoginID."'";
				$scrow = $dsql->GetOne($sql);
				if( $scrow  )
				{
					$this->M_SpaceID = $scrow['uid'];
				}
				$sql = "select count(1) tt from dede_addoninfos where mid={$this->M_ID}";
				$scrow = $dsql->GetOne($sql);
				if( $scrow  )
				{
					$this->M_InfoNumber = $scrow['tt'];
				}

				if( $this->M_SpaceID > 0 )
				{
					// 得到消息数
					$sql = "select count(1) ct from uc_pms where msgtoid = '{$this->UserName}' and `new`=1 and fromappid=4 and related = 1 and subject <>''";
					$scrow = $dsql->GetOne($sql);
					$this->M_MsgNumber= $scrow['ct'];

					// 得到金币数
					$sql = "select extcredits2, posts from cdb_members where uid= {$this->M_SpaceID}";
					
					$scrow = $dsql->GetOne($sql);
					$this->M_Gold= $scrow['extcredits2'];
					$this->M_Posts = $scrow['posts'];
					
				}
				
				if($this->fields['matt']==10)
				{
					$this->isAdmin = true;
				}
			}
			else
			{
				$this->ResetUser();
			}
		}
	}

	function MemberLogin($kptime = -1)
	{
		$this->__construct($kptime);
	}

	//退出cookie的会话
	function ExitCookie()
	{
		$this->ResetUser();
	}

	//验证用户是否已经登录
	function IsLogin()
	{
		if($this->M_ID > 0) return true;
		else return false;
	}

	//检测用户上传空间
	function GetUserSpace()
	{
		global $dsql;
		$uid = $this->M_ID;
		$row = $dsql->GetOne("select sum(filesize) as fs From `#@__uploads` where mid='$uid'; ");
		return $row['fs'];
	}

	function CheckUserSpace()
	{
		global $cfg_mb_max;
		$uid = $this->M_ID;
		$hasuse = $this->GetUserSpace();
		$maxSize = $cfg_mb_max * 1024 * 1024;
		if($hasuse >= $maxSize)
		{
			ShowMsg('你的空间已满，不允许上传新文件！','-1');
			exit();
		}
	}

	//更新用户信息统计表
	function UpdateUserTj($field,$uptype='add')
	{
		global $dsql;
		$mid = $this->M_ID;
		$arr = $dsql->GetOne("Select * `#@__member_tj` where mid='$mid' ");
		if(!is_array($arr))
		{
			$arr = array('article'=>0,'album'=>0,'archives'=>0,'homecount'=>0,'pagecount'=>0,'feedback'=>0,'friend'=>0,'stow'=>0);
		}
		extract($arr);
		if(isset($$field))
		{
			if($uptype=='add')
			{
				$$field++;
			}
			else if($$field > 0)
			{
				$$field--;
			}
		}
		$inquery = "INSERT INTO `#@__member_tj` (`mid`,`article`,`album`,`archives`,`homecount`,`pagecount`,`feedback`,`friend`,`stow`)
               VALUES ('$mid','$article','$album','$archives','$homecount','$pagecount','$feedback','$friend','$stow'); ";
		$dsql->ExecuteNoneQuery("Delete From `#@__member_tj` where mid='$mid' ");
		$dsql->ExecuteNoneQuery($inquery);
	}

	//重置用户信息
	function ResetUser()
	{
		$this->fields = '';
		$this->M_ID = 0;
		$this->M_LoginID = '';
		$this->M_Rank = 0;
		$this->M_Uprank = 0;
		$this->M_Money = 0;
		$this->M_UserName = "";
		$this->M_LoginTime = 0;
		$this->M_MbType = '';
		$this->M_Scores = 0;
		$this->M_Spacesta = -2;
		DropCookie('DedeUserID');
		DropCookie('DedeLoginTime');
	}

	//获取整数值
	function GetNum($fnum){
		$fnum = ereg_replace("[^0-9\.]",'',$fnum);
		return $fnum;
	}

	//用户登录
	//把登录密码转为指定长度md5数据
	function GetEncodePwd($pwd)
	{
		global $cfg_mb_pwdtype;
		if(empty($cfg_mb_pwdtype)) $cfg_mb_pwdtype = '32';
		switch($cfg_mb_pwdtype)
		{
			case 'l16':
				return substr(md5($pwd), 0, 16);
			case 'r16':
				return substr(md5($pwd), 16, 16);
			case 'm16':
				return substr(md5($pwd), 8, 16);
			default:
				return md5($pwd);
		}
	}
	
	//把数据库密码转为特定长度
	//如果数据库密码是明文的，本程序不支持
	function GetShortPwd($dbpwd)
	{
		global $cfg_mb_pwdtype;
		if(empty($cfg_mb_pwdtype)) $cfg_mb_pwdtype = '32';
		$dbpwd = trim($dbpwd);
		if(strlen($dbpwd)==16)
		{
			return $dbpwd;
		}
		else
		{
			switch($cfg_mb_pwdtype)
			{
				case 'l16':
					return substr($dbpwd, 0, 16);
				case 'r16':
					return substr($dbpwd, 16, 16);
				case 'm16':
					return substr($dbpwd, 8, 16);
				default:
					return $dbpwd;
			}
		}
	}
	
	function CheckUser(&$loginuser,$loginpwd)
	{
		global $dsql;

		//检测用户名的合法性
		$rs = CheckUserID($loginuser,'用户名',false);

		//用户名不正确时返回验证错误，原登录名通过引用返回错误提示信息
		if($rs!='ok')
		{
			$loginuser = $rs;
			return '0';
		}

		//matt=10 是管理员关连的前台帐号，为了安全起见，这个帐号只能从后台登录，不能直接从前台登录
		$row = $dsql->GetOne("Select mid,matt,pwd,logintime From `#@__member` where userid like '$loginuser' ");
		if(is_array($row))
		{
			if($this->GetShortPwd($row['pwd']) != $this->GetEncodePwd($loginpwd))
			{
				return -1;
			}
			else
			{
				//管理员帐号不允许从前台登录
				if($row['matt']==10) {
					return -2;
				}
				else {
					$this->PutLoginInfo($row['mid'], $row['logintime']);
					return 1;
				}
			}
		}
		else
		{
			return 0;
		}
	}

	//保存用户cookie
	function PutLoginInfo($uid, $logintime=0)
	{
		global $cfg_login_adds, $dsql;
		//登录增加积分(上一次登录时间必须大于两小时)
		if(time() - $logintime > 7200 && $cfg_login_adds > 0)
		{
			$dsql->ExecuteNoneQuery("Update `#@__member` set `scores`=`scores`+{$cfg_login_adds} where mid='$uid' ");
		}
		$this->M_ID = $uid;
		$this->M_LoginTime = time();
		if($this->M_KeepTime > 0)
		{
			PutCookie('DedeUserID',$uid,$this->M_KeepTime);
			PutCookie('DedeLoginTime',$this->M_LoginTime,$this->M_KeepTime);
		}
		else
		{
			PutCookie('DedeUserID',$uid);
			PutCookie('DedeLoginTime',$this->M_LoginTime);
		}
	}

	//获得会员目前的状态
	function GetSta($dsql)
	{
		$sta = '';
		if($this->M_Rank==0)
		{
			$sta .= "你目前的身份是：普通会员";
		}
		else
		{
			$row = $dsql->GetOne("Select membername From `#@__arcrank` where rank='".$this->M_Rank."'");
			$sta .= "你目前的身份是：".$row['membername'];
		}
		if($this->M_Uprank>0)
		{
			$row = $dsql->GetOne("Select membername From `#@__arcrank` where rank='".$this->M_Uprank."'");
			$mname = $row['membername'];
			$sta .= " 正在申请升级为：$mname ";
		}
		$sta .= " 拥有金币：{$this->M_Money} 个，积分：{$this->M_Scores} 分";
		if($this->M_Upmoney>0)
		{
			$sta .= "，正在申请 ".$this->M_Upmoney." 个金币";
		}
		$sta .= "。";
		return $sta;
	}
}
?>