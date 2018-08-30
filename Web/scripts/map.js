
var mapsToInstance = [];
var mapLibLoaded = false;

class Map
{
    constructor(divID, latitude, longitude, mapZoom)
    {
        this.divID = divID;
        this.zoom = mapZoom;
        this.center = {lat: latitude, lng: longitude};

        if (mapLibLoaded)
            this.init();
        else
            mapsToInstance.add(this);
    }

    init()
    {
        var map = new google.maps.Map(document.getElementById(this.divID),
            {zoom: this.zoom, center: this.center});

        var marker = new google.maps.Marker({position: this.center, map: map});
    }
}
