// TradingView Advanced Charts Integration
const initTradingViewChart = (containerId, symbol, interval = '1D') => {
    new TradingView.widget({
        "container_id": containerId,
        "autosize": true,
        "symbol": symbol,
        "interval": interval,
        "timezone": "Asia/Kolkata",
        "theme": "dark",
        "style": "1",
        "locale": "in",
        "enable_publishing": false,
        "hide_top_toolbar": false,
        "hide_legend": false,
        "save_image": true,
        "studies": [
            "MACD@tv-basicstudies",
            "RSI@tv-basicstudies",
            "VolumeProfite@tv-basicstudies"
        ],
        "show_popup_button": true,
        "popup_width": "1000",
        "popup_height": "650",
        "disabled_features": ["use_localstorage_for_settings"],
        "enabled_features": ["study_templates"],
        "overrides": {
            "mainSeriesProperties.candleStyle.upColor": "#26a69a",
            "mainSeriesProperties.candleStyle.downColor": "#ef5350",
            "mainSeriesProperties.candleStyle.wickUpColor": "#26a69a",
            "mainSeriesProperties.candleStyle.wickDownColor": "#ef5350"
        }
    });
};

// D3.js Advanced Technical Indicators
class TechnicalIndicators {
    constructor(containerId) {
        this.svg = d3.select(`#${containerId}`);
        this.margin = {top: 20, right: 50, bottom: 30, left: 50};
        this.width = +this.svg.attr("width") - this.margin.left - this.margin.right;
        this.height = +this.svg.attr("height") - this.margin.top - this.margin.bottom;
    }

    drawRSI(data) {
        const rsi = technicalindicators.RSI.calculate({
            values: data.map(d => d.close),
            period: 14
        });

        const x = d3.scaleTime()
            .domain(d3.extent(data, d => d.date))
            .range([0, this.width]);

        const y = d3.scaleLinear()
            .domain([0, 100])
            .range([this.height, 0]);

        const line = d3.line()
            .x(d => x(d.date))
            .y(d => y(d.value));

        this.svg.append("path")
            .datum(rsi.map((d, i) => ({date: data[i].date, value: d})))
            .attr("fill", "none")
            .attr("stroke", "#2196f3")
            .attr("stroke-width", 1.5)
            .attr("d", line);

        // Add overbought/oversold lines
        this.svg.append("line")
            .attr("x1", 0)
            .attr("x2", this.width)
            .attr("y1", y(70))
            .attr("y2", y(70))
            .attr("stroke", "#ef5350")
            .attr("stroke-dasharray", "5,5");

        this.svg.append("line")
            .attr("x1", 0)
            .attr("x2", this.width)
            .attr("y1", y(30))
            .attr("y2", y(30))
            .attr("stroke", "#26a69a")
            .attr("stroke-dasharray", "5,5");
    }
}

// Recharts Responsive Components
const CustomAreaChart = ({ data, dataKey, stroke, fill }) => {
    return (
        <ResponsiveContainer width="100%" height={400}>
            <AreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <defs>
                    <linearGradient id={`color${dataKey}`} x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor={fill} stopOpacity={0.8}/>
                        <stop offset="95%" stopColor={fill} stopOpacity={0}/>
                    </linearGradient>
                </defs>
                <XAxis dataKey="date" />
                <YAxis />
                <CartesianGrid strokeDasharray="3 3" />
                <Tooltip 
                    contentStyle={{
                        backgroundColor: '#1a1a1a',
                        border: '1px solid #333',
                        borderRadius: '4px'
                    }}
                />
                <Area 
                    type="monotone" 
                    dataKey={dataKey}
                    stroke={stroke}
                    fillOpacity={1}
                    fill={`url(#color${dataKey})`}
                />
            </AreaChart>
        </ResponsiveContainer>
    );
};

// Professional Volume Profile
class VolumeProfile {
    constructor(containerId) {
        this.container = d3.select(`#${containerId}`);
        this.pocColor = "#f9a825"; // Point of Control color
        this.valueAreaColor = "#4caf50";
    }

    calculate(data, numberOfBuckets = 24) {
        const volumes = data.map(d => ({
            price: d.price,
            volume: d.volume
        }));

        const priceRange = d3.extent(volumes, d => d.price);
        const bucketSize = (priceRange[1] - priceRange[0]) / numberOfBuckets;

        // Create price buckets
        const buckets = Array.from({length: numberOfBuckets}, (_, i) => {
            const bucketStart = priceRange[0] + (i * bucketSize);
            return {
                priceStart: bucketStart,
                priceEnd: bucketStart + bucketSize,
                volume: 0
            };
        });

        // Fill buckets with volume
        volumes.forEach(trade => {
            const bucketIndex = Math.floor((trade.price - priceRange[0]) / bucketSize);
            if (bucketIndex >= 0 && bucketIndex < numberOfBuckets) {
                buckets[bucketIndex].volume += trade.volume;
            }
        });

        // Find Point of Control (POC)
        const poc = buckets.reduce((max, bucket) => 
            bucket.volume > max.volume ? bucket : max
        , buckets[0]);

        // Calculate Value Area (70% of volume)
        const totalVolume = d3.sum(buckets, d => d.volume);
        const valueAreaVolume = totalVolume * 0.7;
        let currentVolume = 0;
        const valueArea = buckets
            .sort((a, b) => b.volume - a.volume)
            .filter(bucket => {
                if (currentVolume < valueAreaVolume) {
                    currentVolume += bucket.volume;
                    return true;
                }
                return false;
            });

        return {
            buckets,
            poc,
            valueArea
        };
    }

    draw(data) {
        const { buckets, poc, valueArea } = this.calculate(data);
        
        const margin = {top: 20, right: 30, bottom: 30, left: 40};
        const width = this.container.node().getBoundingClientRect().width - margin.left - margin.right;
        const height = 400 - margin.top - margin.bottom;

        const svg = this.container.append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);

        const x = d3.scaleLinear()
            .domain([0, d3.max(buckets, d => d.volume)])
            .range([0, width]);

        const y = d3.scaleLinear()
            .domain([d3.min(buckets, d => d.priceStart), d3.max(buckets, d => d.priceEnd)])
            .range([height, 0]);

        // Draw volume bars
        svg.selectAll("rect")
            .data(buckets)
            .enter()
            .append("rect")
            .attr("x", 0)
            .attr("y", d => y(d.priceEnd))
            .attr("width", d => x(d.volume))
            .attr("height", d => y(d.priceStart) - y(d.priceEnd))
            .attr("fill", d => 
                d === poc ? this.pocColor :
                valueArea.includes(d) ? this.valueAreaColor :
                "#666"
            )
            .attr("opacity", 0.6);

        // Add axes
        svg.append("g")
            .attr("transform", `translate(0,${height})`)
            .call(d3.axisBottom(x));

        svg.append("g")
            .call(d3.axisLeft(y));
    }
}

// Export chart components
export {
    initTradingViewChart,
    TechnicalIndicators,
    CustomAreaChart,
    VolumeProfile
};
