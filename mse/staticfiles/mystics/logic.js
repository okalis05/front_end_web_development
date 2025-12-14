// Build the metadata panel
function buildMetadata(sample) {
  d3.json("https://api.balldontlie.io").then((data) => {
     console.log(data)
    // get the metadata field 
    let metadata = data.metadata;
       console.log(metadata)
  
    
    // Filter the metadata for the object with the desired sample number
    let sampleMetadata = metadata.filter(sampleObj => sampleObj.id == sample);
    let sampleMetadata_result = sampleMetadata[0];

    // Use d3 to select the panel with id of `#sample-metadata`
     let metadataId = d3.select("#sample-metadata");

    // Use `.html("") to clear any existing metadata
    metadataId.html("")

    // Inside a loop, you will need to use d3 to append new
    // tags for each key-value in the filtered metadata.
    for (i in sampleMetadata_result){
      metadataId.append("h6").text(`${i.toUpperCase()}: ${sampleMetadata_result[i]}`);
    }

  });
}

// function to build both charts
function buildCharts(sample) {
  d3.json("https://api.balldontlie.io").then((data) => {
    console.log(data);

    // Get the samples field
    let samples = data.samples
    console.log(samples)


    // Filter the samples for the object with the desired sample number
    let dataSample = samples.filter(sampleObj => sampleObj.id == sample);
    let dataSample_result = dataSample[0];


    // Get the otu_ids, otu_labels, and sample_values
    let otu_ids = dataSample_result.otu_ids ;
    let otu_labels = dataSample_result.otu_labels  ;
    let sample_values = dataSample_result.sample_values;

    console.log("Otu IDs:" , otu_ids)
    console.log("Otu Labels:" , otu_labels)
    console.log("Sample Values:" , sample_values)


    // Build a Bubble Chart
    let data1 = [{
      x:otu_ids,
      y:sample_values,
      by:sample_values,
      mode:"markers",
      text: otu_labels,
      marker:{
        size:sample_values,
        color : otu_ids, 
        colorscale:"Earth",
      },
      height:800,
      width:1000,
      type:"bubble"
    }]

     //plot layout
    let layout1 = {
      title :"Bacteria cultures Per Sample",
      xaxis:{title:'OTU ID'},
      yaxis:{title:'Number of Bacteria'},
      hovermode:'closest'
      
    }

    // Render the Bubble Chart
    Plotly.newPlot("bubble" , data1 , layout1);


    // For the Bar Chart, map the otu_ids to a list of strings for your yticks
    let yticks = otu_ids.map(otuID => `OTU ${otuID}`);
    let data2 = [{
      x:sample_values.slice(0,10).reverse(),
      y:yticks.slice(0,10).reverse(),
      text:otu_labels.slice(0,10).reverse(),
      orientation:"h",
      type:"bar",
    }]

 
    // Build a Bar Chart
    // Don't forget to slice and reverse the input data appropriately
    let layout2 = {
      title :"Top 10 Bacteria Cultures Found",
      xaxis:{title:'Number of Bacteria'}
    }


    // Render the Bar Chart
    Plotly.newPlot("bar" , data2 , layout2)

  });
}
// Function to run on page load
function init(){
  d3.json("https://api.balldontlie.io").then((data) => {

    // Get the names field
    let name = data.names
     console.log(name)

    // Use d3 to select the dropdown with id of `#selDataset`
     let dropDownMenu = d3.select("#selDataset");

    // Use the list of sample names to populate the select options
    // Hint: Inside a loop, you will need to use d3 to append a new
    // option for each sample name.
    for (let i=0; i<name.length; i++ ){
      dropDownMenu.append("option").text(name[i]).property("value" , name[i])
    };
     
    // Get the first sample from the list
    let firstSample = name[0];
    console.log("first sample:" , firstSample)


    // Build charts and metadata panel with the first sample
    buildCharts(firstSample);
    buildMetadata(firstSample);
  });
}
// Function for event listener
function optionChanged(newSample){
  console.log("A new selection was made:" , newSample)

  // Build charts and metadata panel each time a new sample is selected
  buildCharts(newSample);
  buildMetadata(newSample);

}
// Initialize the dashboard
init();