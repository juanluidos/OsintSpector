
// datos del grafo

var nodes = new vis.DataSet(
    grafoComunidades["nodes"]);

var edges = new vis.DataSet(
    grafoComunidades["edges"]
);

var options = {
    nodes: {
        shape: "dot",
        size: 10,
        font: {
            size: 12,
            color: "#000000"
        },
        borderWidth: 1,
        borderWidthSelected: 2
    },
    edges: {
        width: 1,
        color: {inherit: "from"},
        smooth: {
            type: "continuous"
        }
    }
};
var grafoComunid = new vis.Network(
    document.getElementById('grafoCo'),
    {nodes: nodes, edges: edges},
    options
);