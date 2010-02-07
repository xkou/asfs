<?php error_reporting(E_ALL) ?> 
<?php
	require_once(dirname(__FILE__)."/config.php");
	CheckRank(0,0);
	require_once(DEDEINC."/typelink.class.php");
	require_once(DEDEINC."/datalistcp.class.php");
	require_once(DEDEMEMBER."/inc/inc_list_functions.php");
	if(!isset($action)) exit(0);
	$query="";
	$mid = $cfg_ml->M_ID;
	if( $action == 'info' )
	{
		$query = "select arc.aid, arc.typeid,arc.senddate,arc.arcrank,arc.click,arc.title, e1.ename name2, e2.ename name1
				from `dede_addoninfos` arc
				left join `dede_sys_enum` e1 on e1.egroup='infotype' and e1.evalue=arc.infotype
				left join `dede_sys_enum` e2 on e2.egroup='infotype' and e2.evalue=FLOOR(arc.infotype/100)*100
				where arc.mid = $mid
				order by arc.aid desc ";
		$positionname='分类信息管理';
	}
	else if( $action=='comment')
	{
		$query = "select p.id, p.aid, p.arctitle, p.ischeck, p.dtime, p.msg from dede_feedback p where mid = $mid order by id desc";
		$positionname='评论管理';

	}
	else if( $action=='biz')
	{
		$query = "select p.aid, p.title, p.click, p.arcrank, p.senddate, e1.ename name1 from dede_addonbiz p 
		left join `dede_sys_enum` e1 on e1.egroup='biztype' and e1.evalue=p.biztype
		where p.mid = $mid order by id desc";
		$positionname='商圈管理';

	}

	$GLOBALS['cfg_tplcache']='N';
	$dlist = new DataListCP();
	$dlist->pageSize = 20;
	$dlist->SetParameter('action',"$action"); 
	$dlist->SetTemplate(DEDEMEMBER."/templets/manager_base.html");
	$dlist->SetSource($query);
	$dlist->Display();
?>
