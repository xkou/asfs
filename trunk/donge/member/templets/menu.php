

<div class="dedeLeft">
	<div class='mark' ></div>
	<ul class="leftShortcut">
		<li class="newinfo"><a href="/member/newinfo.php" >发信息</a> </li>
		<li class='newblog'><a href="/u/cp.php?ac=blog" >发日志</a> </li>
		<li class='newask' ><a href="/ask/post.php" >发问题</a> </li>
	</ul>
    <ul class="leftNav">
		<li class="icon">
			<a href="/member/manager.php?action=info" title="已发布分类广告">管理我的分类广告</a>
		</li>
		<li class="icon">
			<a href="/member/manager.php?action=comment" title="我发布的评论">管理我发的评论</a>
		</li>
		<li class="icon">
			<a href="/member/manager.php?action=biz" title="我发布的评论">管理我发布的商铺</a>
		</li>
		<li class="icon">
			<a href="/bbs/my.php?item=threads" title="已发布论坛发贴">管理我的论坛发贴</a>
		</li>
		<li class="icon">
			<a href="/bbs/magic.php" title="管理我的道具">管理我的道具</a>
		</li>
		<li class="icon">
			<a href="/u/space-blog.html" title="管理我的日志">管理我的日志</a>
		</li>
	
    </ul>
<?php if ( $cfg_ml->IsLogin() ){ ?>
	<ul class="bottommenu">
		<li class="icon"><a href='/bbs/memcp.php?action=profile&typeid=1' >修改密码</a>
		<li class="icon"><a href='/member/index_do.php?fmdo=login&dopost=exit' >退出登陆</a>
	</ul>
 <?php }  ?>
   
</div>


