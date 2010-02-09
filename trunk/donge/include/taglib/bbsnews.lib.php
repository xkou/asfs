<?php
if(!defined('DEDEINC'))
{
	exit("Request Error!");
}
function lib_bbsnews(&$ctag,&$refObj)
{
	global $dsql,$envs;
	
	//属性处理
	$attlist="row|4,titlelen|24,typeid|0";
	FillAttsDefault($ctag->CAttribute->Items,$attlist);
	extract($ctag->CAttribute->Items, EXTR_SKIP);
	$revalue = '';
	$Innertext = trim($ctag->GetInnerText());
	if(empty($sqlCt)) 
		$sqlCt = 0;

	$ctp = new DedeTagParse();
	$ctp->SetNameSpace('field','[',']');
	$ctp->LoadSource($Innertext);

	$thisrs = 'sq'.$sqlCt;
	$wheresql="";
	if( !empty( $typeid )) 
		$wheresql="where fid=".$typeid;

	$sql="select tid, author, subject, dateline, highlight+1 hl from cdb_threads ".$wheresql." order by tid desc limit ".$row ;
	$dsql->Execute($thisrs,$sql);
	while($rowa = $dsql->GetArray($thisrs))
	{
		$rowa['acturl']="/bbs/viewthread.php?tid=".$rowa["tid"];
		//$row['hl'] = $row['hl']==0;
		$rowa['senddate']=GetDateMK( $rowa['dateline'] );
		
		foreach($ctp->CTags as $tagid=>$ctag)
		{
			if( !empty($rowa[$ctag->GetName()]) )
			{ 
				$ctp->Assign($tagid,$rowa[$ctag->GetName()]);
			}
		}
		
		$revalue .= $ctp->GetResult();
	}
	
	
	//你需编写的代码，不能用echo之类语法，把最终返回值传给$revalue
	//------------------------------------------------------
	

	
	//------------------------------------------------------
	return $revalue;
}
?>