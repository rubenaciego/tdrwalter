<!DOCTYPE html>
<html lang="cat">
	
	<?php $data = fread(fopen("../register.json", "r"), filesize("../register.json")); ?>
	
    <head>
		<title>WALTER</title>
		<meta charset="UTF-8">

		<script src="https://code.jquery.com/jquery-3.3.1.min.js"></script>
		<script src="scripts/map.js"></script>
		<script src="scripts/main.js"></script>
		<script async defer src="https://maps.googleapis.com/maps/api/js?key=AIzaSyC4ymxi7xez0mGDejD1NyazJkc_3GSco_Q&callback=initMaps"></script>

		<script>
			var data = <?php echo $data;?>;
		</script>

		<link rel="stylesheet" href="styles/main.css">
    </head>

    <body>
	<div style="padding: 10px;">
	<div class="topnav">
		<a class="active" href="index.php">Inici</a>
		<a href="data.html">Dades que s'estudien</a>
		<a href="about.html">Informació sobre el projecte</a>
	</div>
		<br/>
		<p>Dades recollides</p>
		<table id="data"></table>
		<p>Gràfic</p>
		<div id="images"></div>
		<p>Ubicació actual</p>
		<div id="map"></div>

		</div>
    </body>

</html>
