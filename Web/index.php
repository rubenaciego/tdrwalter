<!DOCTYPE HTML>
<html>
	
	<?php $data = fread(fopen("../register.json", "r"), filesize("../register.json")); ?>
	
    <head>
        <title>WALTER</title>

		<script src="https://code.jquery.com/jquery-3.3.1.min.js"></script>
		<script src="scripts/map.js"></script>
		<script src="scripts/main.js"></script>
		<script async defer src="https://maps.googleapis.com/maps/api/js?key=AIzaSyC4ymxi7xez0mGDejD1NyazJkc_3GSco_Q&callback=initMaps"></script>

		<script>
			var data = <?php echo $data;?>;
		</script>
    </head>

    <body>
		<p>Dades recollides</p>
		<table id="data" border="2"></table>
		<p>Imatges</p>
		<div id="images"></div>
		<div id="map" style="height: 400px; width: 400px;"></div>
    </body>

</html>
