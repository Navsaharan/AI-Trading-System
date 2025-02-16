class ThemeManager {
    constructor() {
        this.isDarkMode = localStorage.getItem('theme') === 'dark';
        this.init();
    }

    init() {
        // Create theme toggle button
        this.createToggleButton();
        
        // Apply saved theme
        this.applyTheme(this.isDarkMode);
        
        // Start color auto-adjustment
        this.startColorAdjustment();
    }

    createToggleButton() {
        const button = document.createElement('button');
        button.className = 'theme-toggle';
        button.innerHTML = `
            <div class="theme-toggle-icon">
                <svg class="sun-icon" viewBox="0 0 24 24">
                    <path d="M12 7c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zM2 13h2c.55 0 1-.45 1-1s-.45-1-1-1H2c-.55 0-1 .45-1 1s.45 1 1 1zm18 0h2c.55 0 1-.45 1-1s-.45-1-1-1h-2c-.55 0-1 .45-1 1s.45 1 1 1zM11 2v2c0 .55.45 1 1 1s1-.45 1-1V2c0-.55-.45-1-1-1s-1 .45-1 1zm0 18v2c0 .55.45 1 1 1s1-.45 1-1v-2c0-.55-.45-1-1-1s-1 .45-1 1zM5.99 4.58c-.39-.39-1.03-.39-1.41 0-.39.39-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0s.39-1.03 0-1.41L5.99 4.58zm12.37 12.37c-.39-.39-1.03-.39-1.41 0-.39.39-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0 .39-.39.39-1.03 0-1.41l-1.06-1.06zm1.06-10.96c.39-.39.39-1.03 0-1.41-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06zM7.05 18.36c.39-.39.39-1.03 0-1.41-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06z"/>
                </svg>
                <svg class="moon-icon" viewBox="0 0 24 24">
                    <path d="M9.37,5.51C9.19,6.15,9.1,6.82,9.1,7.5c0,4.08,3.32,7.4,7.4,7.4c0.68,0,1.35-0.09,1.99-0.27C17.45,17.19,14.93,19,12,19 c-3.86,0-7-3.14-7-7C5,9.07,6.81,6.55,9.37,5.51z M12,3c-4.97,0-9,4.03-9,9s4.03,9,9,9s9-4.03,9-9c0-0.46-0.04-0.92-0.1-1.36 c-0.98,1.37-2.58,2.26-4.4,2.26c-2.98,0-5.4-2.42-5.4-5.4c0-1.81,0.89-3.42,2.26-4.4C12.92,3.04,12.46,3,12,3L12,3z"/>
                </svg>
            </div>
        `;
        
        button.addEventListener('click', () => this.toggleTheme());
        document.body.appendChild(button);
    }

    toggleTheme() {
        this.isDarkMode = !this.isDarkMode;
        this.applyTheme(this.isDarkMode);
        localStorage.setItem('theme', this.isDarkMode ? 'dark' : 'light');
    }

    applyTheme(isDark) {
        const root = document.documentElement;
        const transitionClass = 'theme-transition';
        
        // Add transition class
        document.body.classList.add(transitionClass);
        
        if (isDark) {
            document.body.classList.add('dark-mode');
            this.updateChartThemes('dark');
        } else {
            document.body.classList.remove('dark-mode');
            this.updateChartThemes('light');
        }
        
        // Remove transition class after animation
        setTimeout(() => {
            document.body.classList.remove(transitionClass);
        }, 300);
    }

    updateChartThemes(theme) {
        // Update TradingView charts
        const tvCharts = document.querySelectorAll('.tradingview-chart');
        tvCharts.forEach(chart => {
            if (chart.chart) {
                chart.chart.changeTheme(theme);
            }
        });

        // Update D3 charts
        const d3Charts = document.querySelectorAll('.d3-chart');
        d3Charts.forEach(chart => {
            this.updateD3ChartTheme(chart, theme);
        });

        // Update Recharts
        const reCharts = document.querySelectorAll('.recharts-wrapper');
        reCharts.forEach(chart => {
            this.updateRechartsTheme(chart, theme);
        });
    }

    updateD3ChartTheme(chart, theme) {
        const colors = theme === 'dark' ? {
            background: '#1a1a1a',
            text: '#ffffff',
            grid: '#404040',
            line: '#2196f3'
        } : {
            background: '#ffffff',
            text: '#1a1a1a',
            grid: '#e0e0e0',
            line: '#2196f3'
        };

        // Update D3 chart elements
        chart.style.background = colors.background;
        
        const svg = chart.querySelector('svg');
        if (svg) {
            // Update axes
            svg.querySelectorAll('.axis text').forEach(text => {
                text.style.fill = colors.text;
            });
            
            // Update grid lines
            svg.querySelectorAll('.grid line').forEach(line => {
                line.style.stroke = colors.grid;
            });
            
            // Update lines
            svg.querySelectorAll('.line').forEach(line => {
                line.style.stroke = colors.line;
            });
        }
    }

    updateRechartsTheme(chart, theme) {
        const colors = theme === 'dark' ? {
            text: '#ffffff',
            grid: '#404040',
            tooltip: '#2d2d2d'
        } : {
            text: '#1a1a1a',
            grid: '#e0e0e0',
            tooltip: '#ffffff'
        };

        // Update Recharts elements
        chart.querySelectorAll('.recharts-text').forEach(text => {
            text.style.fill = colors.text;
        });
        
        chart.querySelectorAll('.recharts-cartesian-grid-horizontal line, .recharts-cartesian-grid-vertical line').forEach(line => {
            line.style.stroke = colors.grid;
        });
        
        const tooltip = chart.querySelector('.recharts-tooltip-wrapper');
        if (tooltip) {
            tooltip.style.background = colors.tooltip;
        }
    }

    startColorAdjustment() {
        // Monitor contrast ratios
        setInterval(() => {
            this.adjustColors();
        }, 1000);
    }

    adjustColors() {
        const elements = document.querySelectorAll('*');
        elements.forEach(element => {
            const style = window.getComputedStyle(element);
            const backgroundColor = style.backgroundColor;
            const color = style.color;
            
            // Calculate contrast ratio
            const contrast = this.calculateContrastRatio(backgroundColor, color);
            
            // If contrast is too low, adjust colors
            if (contrast < 4.5) {
                const newColor = this.improveContrast(backgroundColor, color);
                element.style.color = newColor;
            }
        });
    }

    calculateContrastRatio(bg, fg) {
        const getBrightness = color => {
            const rgb = color.match(/\d+/g);
            if (!rgb) return 0;
            return (parseInt(rgb[0]) * 299 + parseInt(rgb[1]) * 587 + parseInt(rgb[2]) * 114) / 1000;
        };
        
        const bgBrightness = getBrightness(bg);
        const fgBrightness = getBrightness(fg);
        
        const lighter = Math.max(bgBrightness, fgBrightness);
        const darker = Math.min(bgBrightness, fgBrightness);
        
        return (lighter + 0.05) / (darker + 0.05);
    }

    improveContrast(bg, fg) {
        const getBrightness = color => {
            const rgb = color.match(/\d+/g);
            if (!rgb) return 0;
            return (parseInt(rgb[0]) * 299 + parseInt(rgb[1]) * 587 + parseInt(rgb[2]) * 114) / 1000;
        };
        
        const bgBrightness = getBrightness(bg);
        
        // If background is dark, make text lighter
        if (bgBrightness < 128) {
            return '#ffffff';
        }
        // If background is light, make text darker
        return '#000000';
    }
}

// Initialize theme manager
document.addEventListener('DOMContentLoaded', () => {
    window.themeManager = new ThemeManager();
});
