'use strict';

var config = {
	totalWidth: 1100,
	totalHeight: 450,
	margin: {
		top: 40,
		right: 20,
		bottom: 30,
		left: 100
	},
	pointRadius: 4,
	transitionTime: 0,
	formatParseDate: '%Y/%m/%d %H:%M:%S',
	formatParseDetailTime: '%Y/%m/%d %H:%M:%S',
	formatToDetailTime: '%Y/%m/%d %H:%M',

	lineChartID: 'linechart-id',
	toolTipID: 'linechart-tooltip-id',
	lineChartHelperID: 'linechart-helper-id',
	noDataTextID: 'linechart-nodatatext-id',
	yAxisLabelID: 'linechart-yaxislabel-id',
	circleID: 'linechart-circle-id'
}

var loadingHTML =
'<div>' +
'  <span class="glyphicon glyphicon-refresh glyphicon-refresh-animate">' +
'  </span>' +
'</div>';

var idSelector = function(id) {
	return '#' + id;
}

var handleMouseEvent = {
	initialize: function(d3) {
		this.d3 = d3;
		this.createToolTip();
	},
	createToolTip: function() {
		this.d3.select(idSelector(config.lineChartID))
			.append('div')
				.attr('id', config.toolTipID)
				.style('opacity', 0);
	},
	mouseover: function(element, data) {
		this.d3.select(idSelector(config.lineChartID))
			.style('cursor', 'pointer');
		element
			.attr('r', (element.attr('r') * 1.4))
			.transition().duration(config.transitionTime);
		this.showToolTip(data);
		this.drawLinesToAxes(element, 'x', 0 + config.margin.left);

		var height = config.totalHeight - config.margin.top - config.margin.bottom;
		this.drawLinesToAxes(element, 'y', height + config.margin.top);
	},
	mouseleave: function(element) {
		this.d3.select(idSelector(config.lineChartID))
			.style('cursor', 'default');
		element
			.attr('r', config.pointRadius)
			.transition().duration(config.transitionTime);
		this.earseLinesToAxes();
		this.hideToolTip();
	},
	drawLinesToAxes: function(element, axis, finalPos) {
		var offset = +element.attr('r') + 1;
		if (axis === 'x') {
			var xPos = +element.attr('cx') - offset + config.margin.left,
				yPos = +element.attr('cy') + config.margin.top;
		} else {
			var xPos = +element.attr('cx') + config.margin.left,
				yPos = +element.attr('cy') + offset + config.margin.top;
		}
		this.d3.select(idSelector(config.lineChartID) + ' svg')
			.append('line')
				.attr('id', config.lineChartHelperID)
				.attr('x1', xPos)
				.attr('x2', xPos)
				.attr('y1', yPos)
				.attr('y2', yPos)
				.attr(axis + '1', finalPos)
				.transition().duration(config.transitionTime);
	},
	earseLinesToAxes: function() {
		this.d3.selectAll(idSelector(config.lineChartHelperID)).remove();
	},
	getToolTipHTML: function(d3, d) {
		var formatDetailTime = d3.time.format(config.formatToDetailTime);
		var tooltipHTML =
			'Departure time: ' + formatDetailTime(d.departure_detail_time) + '<br/>' +
			'Arrival time: ' + formatDetailTime(d.arrival_detail_time) + '<br/>' +
			'airline number: ' + d.air_number + '<br/>' +
			'money: ' + '('+ d.currency + ') ' + d.money + '<br/>';
		return tooltipHTML;
	},
	showToolTip: function(data) {
		this.d3.select(idSelector(config.toolTipID))
			.html(this.getToolTipHTML(this.d3, data))
				.style('left', (this.d3.event.pageX) + 'px')
				.style('top', (this.d3.event.pageY - 28) + 'px')
				.style('opacity', .9)
				.transition().duration(config.transitionTime);
	},
	hideToolTip: function() {
		this.d3.select(idSelector(config.toolTipID))
			.style('opacity', 0)
			.transition().duration(config.transitionTime);
	}
}

angular.module('wacouLineChart', ['d3'])

.directive('wacouLinechart', ['d3Service', function(d3Service) {
	return {
		restrict: 'EA',
		scope: {
			data: '='
		},
		link: function(scope, element, attrs) {
			var svgTag = angular.element(loadingHTML);
			var div = angular.element(svgTag).appendTo(element[0]);

			d3Service.d3().then(function(d3) {
				d3.select(element[0])
					.attr('id', config.lineChartID);

				handleMouseEvent.initialize(d3);

				var parseDate = d3.time.format(config.formatParseDate).parse;
				var parseDetailTime = d3.time.format(config.formatParseDetailTime).parse;

				var x = d3.time.scale()
					.range([0, config.totalWidth - config.margin.left - config.margin.right]);
				var y = d3.scale.linear()
					.range([config.totalHeight - config.margin.top - config.margin.bottom, 0]);

				var xAxis = d3.svg.axis().scale(x)
					.orient('bottom').ticks(5);
				var yAxis = d3.svg.axis().scale(y)
					.orient('left').ticks(5);

				var valueline = d3.svg.line()
					.x(function(d) { return x(d.departure_date); })
					.y(function(d) { return y(d.money); });

				var svg = d3.select(element[0])
					.append('svg')
						.attr('width', config.totalWidth)
						.attr('height', config.totalHeight)
					.append('g')
						.attr('transform',
							  'translate(' + config.margin.left + ',' + config.margin.top + ')');

				window.onresize = function() {
					scope.$apply();
				};
				scope.$watch('data', function(newVals, oldVals) {
					scope.render(newVals);
				});
				scope.render = function(data) {
					svg.selectAll('*').remove();

					if (null == data || null == data.length || 0 == data.length) {
						svg.append('text')
							.attr('id', config.noDataTextID)
							.attr('x', config.totalWidth/2 - config.margin.left - 80)
							.attr('y', config.totalHeight/2 - 14)
							.text('I have no data');
					} else {
						var airData = [];
						data.forEach(function(d) {
							var entry = {};
							var rawData = d;
							if (null == rawData.departure_time) {
								return;
							}

							entry = {
								'departure_date': parseDate(rawData.departure_time),
								'arrival_date': parseDate(rawData.arrival_time),
								'arrival_detail_time': parseDetailTime(rawData.arrival_time),
								'departure_detail_time': parseDetailTime(rawData.departure_time),
								'air_number': rawData.air_number,
								'currency': rawData.currency,
								'money': +rawData.money
							}
							airData.push(entry);
						});

						// Scale the range of the data
						x.domain(d3.extent(airData, function(d) { return d.departure_date; }));
						y.domain([0, d3.max(airData, function(d) { return d.money; })]);

						// Add the valueline path.
						svg.append('path')
							.attr('class', 'line')
							.attr('d', valueline(airData));

						var height = config.totalHeight - config.margin.top - config.margin.bottom;
						// Add the X Axis
						svg.append('g')
							.attr('class', 'x axis')
							.attr('transform', 'translate(0,' + height + ')')
							.call(xAxis);

						// Add the Y Axis
						svg.append('g')
							.attr('class', 'y axis')
							.call(yAxis);

						svg.append('text')
							.attr('id', config.yAxisLabelID)
							.attr('transform', 'translate(' + (-33) + ',' + 0 + ')')
							.text(airData[0]['currency']);

						svg.selectAll('dot').data(airData)
							.enter()
							.append('circle')
								.attr('id', config.circleID)
								.attr('r', config.pointRadius)
								.attr('cx', function(d) { return x(d.departure_date); })
								.attr('cy', function(d) { return y(d.money); })
							.on('mouseover', function(d) {
								handleMouseEvent.mouseover(d3.select(this), d);
							})
							.on('mouseout', function(d) {
								handleMouseEvent.mouseleave(d3.select(this));
							});
					}
				} //finish render
				div.remove();
			}); //finish d3 promise then
		} //finish link
	};
}]);
