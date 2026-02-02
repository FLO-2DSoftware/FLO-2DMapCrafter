<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.34" styleCategories="AllStyleCategories">
  <pipe>
    <rasterrenderer type="singlebandpseudocolor"
                    band="1"
                    opacity="1"
                    classificationMin="0"
                    classificationMax="10">
      <rastershader>
        <colorrampshader colorRampType="DISCRETE" classificationMode="Continuous">
          <item value="0.0" label="No scour" color="#1f4e79" alpha="0"/>
          <item value="0.5" label="Minor scour (&lt; 0.5 ft)" color="#7fb3d5"/>
          <item value="2.0" label="Moderate scour (0.5 - 2 ft)" color="#f7dc6f"/>
          <item value="5.0" label="Severe scour (2 - 5 ft)" color="#f39c12"/>
          <item value="10.0" label="Critical scour (5 - 10 ft)" color="#c0392b"/>
          <item value="9999" label="(&gt; 10.0 ft)" color="#7b0000"/>
        </colorrampshader>
      </rastershader>
    </rasterrenderer>
  </pipe>

  <customproperties>
    <property key="NoDataValue" value="-9999"/>
  </customproperties>

  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerTransparency>0</layerTransparency>
</qgis>
