<?php
require_once(dirname(__FILE__)."/config.php");
AjaxHead();
if($myurl == '')
{
	exit('');
}
$uid  = $cfg_ml->M_LoginID;
$face = $cfg_ml->fields['face'] == '' ? $GLOBALS['cfg_memberurl'].'/res/nopic.gif' : $cfg_ml->fields['face'];
if( strpos($face,"avatar.php") ) $face=get_ucface( $cfg_ml->M_SpaceID );
 $pmnum = $cfg_ml->M_MsgNumber == 0?"0":$cfg_ml->M_MsgNumber;
?>
<div class="userinfo">
    <div class="welcome">你好：<strong><?php echo $cfg_ml->M_UserName; ?></strong>，欢迎登录 </div>
    <div class="userface">
        <a href="/u/space.php"><img src="<?php echo $face;?>" width="52" height="52" /></a>
    </div>
    <div class="mylink">
	<?php if( $cfg_ml->M_SpaceID ){ ?>
        <ul>
            <li><a <?php if($pmnum ==0) echo 'href="/u/space.php?do=pm"' ; ?> <?php if($pmnum) echo " href='/u/space.php?do=pm&filter=newpm' style='color:red'" ?> >未读短消息: <?php echo $pmnum; ?> 条</a></li>
            <li><a href="/bbs/memcp.php?action=credits">我的东阿币: <?php echo strval($cfg_ml->M_Gold==0?'0':$cfg_ml->M_Gold) ?> 金</a></li>
            
           
			<?php if ( $cfg_ml->M_Rank == 12 )  { ?>
			<li><strong><a href="/member/checkarticle.php"><font color=red>审核文章</font></a></strong></li>
			<?php }else{ ?>
			<li><a href="/bbs/">论坛发贴数: <?php echo strval($cfg_ml->M_Posts==0?'0':$cfg_ml->M_Posts) ?> 条</a></li>
			<?php } ?>
           
        </ul>
	<?php }else{ ?>
		<a href="/bbs/logging.php?action=login" style='color:red' >激活论坛账号</a>
	<?php } ?>
    </div>
    <div class="uclink">
	<?php if( $cfg_ml->M_SpaceID ){ ?>
        <a href="/member/">会员中心</a> | 
        <a href="/u/cp.php?ac=profile">资料</a> | 
		<a href="/u/">空间</a>  |
       <!-- <a href="<?php echo $myurl;?>">空间</a> | -->
        <a href="<?php echo $cfg_memberurl; ?>/index_do.php?fmdo=login&dopost=exit">退出登录</a> 
	<?php } ?>
    </div>
</div><!-- /userinfo -->