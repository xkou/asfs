<?php
if(!defined('DEDEINC'))
{
	exit("Request Error!");
}
require_once(DEDEINC."/dedetag.class.php");
require_once(DEDEINC."/typelink.class.php");
require_once(DEDEINC."/channelunit.func.php");

@set_time_limit(0);
class RssView
{
	var $dsql;
	var $TypeID;
	var $TypeLink;
	var $TypeFields;
	var $MaxRow;
	var $dtp;
	//php5构造函数
	function __construct($typeid,$max_row=50)
	{
		$this->TypeID = $typeid;
		$this->dtp = new DedeTagParse();
		$this->dtp->refObj = $this;
		$templetfiles = $GLOBALS['cfg_basedir'].$GLOBALS['cfg_templets_dir']."/plus/rss.htm";
		$this->dtp->LoadTemplate($templetfiles);
		$this->dsql = $GLOBALS['dsql'];
		$this->TypeLink = new TypeLink($typeid);
		$this->TypeFields = $this->TypeLink->TypeInfos;
		$this->MaxRow = $max_row;
		$this->TypeFields['title'] = $this->TypeLink->GetPositionLink(false);
		$this->TypeFields['title'] = ereg_replace("[<>]"," / ",$this->TypeFields['title']);
		$this->TypeFields['typelink'] = $GLOBALS['cfg_basehost'].$this->TypeLink->GetOneTypeUrl($this->TypeFields);
		$this->TypeFields['powerby'] = $GLOBALS['cfg_powerby'];
		$this->TypeFields['adminemail'] = $GLOBALS['cfg_adminemail'];
		foreach($this->TypeFields as $k=>$v)
		{
			$this->TypeFields[$k] = htmlspecialchars($v);
		}
		$this->ParseTemplet();
	}

	//php4构造函数
	function RssView($typeid,$max_row=50)
	{
		$this->__construct($typeid,$max_row);
	}

	//关闭相关资源
	function Close()
	{
	}

	//显示列表
	function Display()
	{
		$this->dtp->Display();
	}

	//开始创建列表
	function MakeRss()
	{
		$murl = $GLOBALS['cfg_cmspath']."/data/rss/".$this->TypeID.".xml";
		$mfile = $GLOBALS['cfg_basedir'].$murl;
		$this->dtp->SaveTo($mfile);
		return $murl;
	}

	//解析模板
	function ParseTemplet()
	{
		foreach($this->dtp->CTags as $tid => $ctag)
		{
			if($ctag->GetName()=="field")
			{
				$this->dtp->Assign($tid,$this->TypeFields[$ctag->GetAtt('name')]);
			}
			else if($ctag->GetName()=="rssitem")
			{
				$this->dtp->Assign($tid,
				$this->GetArcList($ctag->GetInnerText())
				);
			}
		}
	}

	//获得文档列表
	function GetArcList($innertext="")
	{
		$typeid=$this->TypeID;
		$innertext = trim($innertext);
		if($innertext=="")
		{
			$innertext = GetSysTemplets("rss.htm");
		}
		$orwhere = " arc.arcrank > -1 ";
		$orwhere .= " And (arc.typeid in (".GetSonIds($this->TypeID,$this->TypeFields['channeltype']).") ) ";
		$ordersql=" order by arc.id desc";
		$query = "Select arc.*,tp.typedir,tp.typename,tp.isdefault,
		tp.defaultname,tp.namerule,tp.namerule2,tp.ispart,tp.moresite,tp.siteurl,tp.sitepath
		from `#@__archives` arc left join `#@__arctype` tp on arc.typeid=tp.id
		where $orwhere $ordersql limit 0,".$this->MaxRow;
		$this->dsql->SetQuery($query);
		$this->dsql->Execute('al');
		$artlist = '';
		$dtp2 = new DedeTagParse();
		$dtp2->SetNameSpace('field','[',']');
		$dtp2->LoadSource($innertext);
		while($row = $this->dsql->GetArray('al'))
		{
			//处理一些特殊字段
			if($row['litpic'] == '-' || $row['litpic'] == '')
			{
				$row['litpic'] = $GLOBALS['cfg_cmspath'].'/images/defaultpic.gif';
			}
			if(!eregi("^http://",$row['litpic']) && $GLOBALS['cfg_multi_site'] == 'Y')
			{
				$row['litpic'] = $GLOBALS['cfg_mainsite'].$row['litpic'];
			}
			$row['picname'] = $row['litpic'];
			$row["arcurl"] = GetFileUrl($row["id"],$row["typeid"],$row["senddate"],$row["title"],
			$row["ismake"],$row["arcrank"],$row["namerule"],$row["typedir"],$row["money"],$row['filename'],$row["moresite"],$row["siteurl"],$row["sitepath"]);
			$row["typeurl"] = GetTypeUrl($row["typeid"],$row["typedir"],$row["isdefault"],$row["defaultname"],$row["ispart"],
			$row["namerule2"],$row["moresite"],$row["siteurl"],$row["sitepath"]);
			$row["info"] = $row["description"];
			$row["filename"] = $row["arcurl"];
			$row["stime"] = GetDateMK($row["pubdate"]);
			$row["image"] = "<img src='".$row["picname"]."' border='0'>";
			$row["fullurl"] = $GLOBALS["cfg_basehost"].$row["arcurl"];
			$row["phpurl"] = $GLOBALS["cfg_plus_dir"];
			$row["templeturl"] = $GLOBALS["cfg_templets_dir"];
			if($row["source"]=='')
			{
				$row["source"] = $GLOBALS['cfg_webname'];
			}
			if($row["writer"]=='')
			{
				$row["writer"] = "秩名";
			}
			foreach($row as $k=>$v)
			{
				$row[$k] = htmlspecialchars($v);
			}
			if(is_array($dtp2->CTags))
			{
				foreach($dtp2->CTags as $k=>$ctag)
				{
					if($ctag->GetName()=='array')
					{

						//传递整个数组，在runphp模式中有特殊作用
						$dtp2->Assign($k,$row);
					}
					else
					{
						if(isset($row[$ctag->GetName()]))
						{
							$dtp2->Assign($k,$row[$ctag->GetName()]);
						}
						else
						{
							$dtp2->Assign($k,'');
						}
					}
				}
			}
			$artlist .= $dtp2->GetResult()."\r\n";
		}
		$this->dsql->FreeResult('al');
		return $artlist;
	}
}//End Class
?>