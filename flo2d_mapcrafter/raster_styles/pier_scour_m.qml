<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.34" styleCategories="AllStyleCategories">
  <pipe>
    <rasterrenderer type="singlebandpseudocolor"
                    band="1"
                    opacity="1"
                    classificationMin="0"
                    classificationMax="3.0">
      <rastershader>
        <colorrampshader colorRampType="DISCRETE" classificationMode="Continuous">
          <item value="0.0" label="No scour" color="#1f4e79" alpha="0"/>
          <item value="0.15" label="Minor scour (&lt; 0.15 m)" color="#7fb3d5"/>
          <item value="0.60" label="Moderate scour (0.15 – 0.60 m)" color="#f7dc6f"/>
          <item value="1.50" label="Severe scour (0.60 – 1.50 m)" color="#f39c12"/>
          <item value="3.00" label="Critical scour (1.50 – 3.00) m" color="#c0392b"/>
          <item value="9999" label="(&gt; 3.00 m)" color="#7b0000"/>
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
