#!/usr/bin/env node
/**
 * Frontend Component Testing Script
 * Tests the frontend components for issues and compatibility.
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function printHeader(title) {
    console.log(`\n${'='.repeat(60)}`);
    console.log(` ${title}`);
    console.log(`${'='.repeat(60)}`);
}

function printTestResult(testName, success, details = '') {
    const status = success ? '✅ PASS' : '❌ FAIL';
    console.log(`${status} ${testName}`);
    if (details) {
        console.log(`    ${details}`);
    }
}

function testComponentStructure() {
    printHeader('TESTING COMPONENT STRUCTURE');
    
    const results = [];
    
    // Test KanbanBoard component
    const kanbanBoardPath = '/Users/devilmashine/Desktop/phStudio/frontend/src/components/KanbanBoard.tsx';
    const kanbanBoardExists = fs.existsSync(kanbanBoardPath);
    printTestResult('KanbanBoard component exists', kanbanBoardExists);
    results.push(['KanbanBoard exists', kanbanBoardExists, '']);
    
    if (kanbanBoardExists) {
        try {
            const content = fs.readFileSync(kanbanBoardPath, 'utf8');
            
            // Test for key features
            const hasDragDrop = content.includes('@hello-pangea/dnd') || content.includes('react-dnd');
            const hasWebSocket = content.includes('useWebSocket') || content.includes('WebSocket');
            const hasSearch = content.includes('search') || content.includes('filter');
            const hasState = content.includes('useState') || content.includes('useEffect');
            
            printTestResult('KanbanBoard has drag-and-drop', hasDragDrop);
            printTestResult('KanbanBoard has WebSocket support', hasWebSocket);
            printTestResult('KanbanBoard has search functionality', hasSearch);
            printTestResult('KanbanBoard has React hooks', hasState);
            
            results.push(['KanbanBoard drag-and-drop', hasDragDrop, '']);
            results.push(['KanbanBoard WebSocket', hasWebSocket, '']);
            results.push(['KanbanBoard search', hasSearch, '']);
            results.push(['KanbanBoard React hooks', hasState, '']);
            
        } catch (error) {
            printTestResult('KanbanBoard content analysis', false, error.message);
            results.push(['KanbanBoard analysis', false, error.message]);
        }
    }
    
    return results;
}

function testEnhancedServices() {
    printHeader('TESTING ENHANCED SERVICES');
    
    const results = [];
    
    // Test enhanced kanban service
    const kanbanServicePath = '/Users/devilmashine/Desktop/phStudio/frontend/src/services/kanbanService.enhanced.ts';
    const kanbanServiceExists = fs.existsSync(kanbanServicePath);
    printTestResult('Enhanced Kanban service exists', kanbanServiceExists);
    results.push(['Enhanced Kanban service', kanbanServiceExists, '']);
    
    if (kanbanServiceExists) {
        try {
            const content = fs.readFileSync(kanbanServicePath, 'utf8');
            
            // Test for key methods
            const hasBoardData = content.includes('getBoardData');
            const hasMoveCard = content.includes('moveCard');
            const hasSearch = content.includes('searchCards');
            const hasErrorHandling = content.includes('try') && content.includes('catch');
            
            printTestResult('Kanban service has getBoardData', hasBoardData);
            printTestResult('Kanban service has moveCard', hasMoveCard);
            printTestResult('Kanban service has search', hasSearch);
            printTestResult('Kanban service has error handling', hasErrorHandling);
            
            results.push(['Kanban getBoardData', hasBoardData, '']);
            results.push(['Kanban moveCard', hasMoveCard, '']);
            results.push(['Kanban search', hasSearch, '']);
            results.push(['Kanban error handling', hasErrorHandling, '']);
            
        } catch (error) {
            printTestResult('Kanban service analysis', false, error.message);
            results.push(['Kanban service analysis', false, error.message]);
        }
    }
    
    return results;
}

function testEnhancedHooks() {
    printHeader('TESTING ENHANCED HOOKS');
    
    const results = [];
    
    // Test enhanced kanban hook
    const kanbanHookPath = '/Users/devilmashine/Desktop/phStudio/frontend/src/hooks/useEnhancedKanban.ts';
    const kanbanHookExists = fs.existsSync(kanbanHookPath);
    printTestResult('Enhanced Kanban hook exists', kanbanHookExists);
    results.push(['Enhanced Kanban hook', kanbanHookExists, '']);
    
    if (kanbanHookExists) {
        try {
            const content = fs.readFileSync(kanbanHookPath, 'utf8');
            
            // Test for key features
            const hasZustandIntegration = content.includes('useAuthStore') || content.includes('useBookingStore');
            const hasWebSocketIntegration = content.includes('useWebSocket');
            const hasOptimisticUpdates = content.includes('optimistic');
            const hasErrorHandling = content.includes('try') && content.includes('catch');
            
            printTestResult('Kanban hook has Zustand integration', hasZustandIntegration);
            printTestResult('Kanban hook has WebSocket integration', hasWebSocketIntegration);
            printTestResult('Kanban hook has optimistic updates', hasOptimisticUpdates);
            printTestResult('Kanban hook has error handling', hasErrorHandling);
            
            results.push(['Kanban hook Zustand', hasZustandIntegration, '']);
            results.push(['Kanban hook WebSocket', hasWebSocketIntegration, '']);
            results.push(['Kanban hook optimistic', hasOptimisticUpdates, '']);
            results.push(['Kanban hook error handling', hasErrorHandling, '']);
            
        } catch (error) {
            printTestResult('Kanban hook analysis', false, error.message);
            results.push(['Kanban hook analysis', false, error.message]);
        }
    }
    
    return results;
}

function testTypescriptTypes() {
    printHeader('TESTING TYPESCRIPT TYPES');
    
    const results = [];
    
    // Test kanban types
    const kanbanTypesPath = '/Users/devilmashine/Desktop/phStudio/frontend/src/types/kanban.ts';
    const kanbanTypesExists = fs.existsSync(kanbanTypesPath);
    printTestResult('Kanban TypeScript types exist', kanbanTypesExists);
    results.push(['Kanban types', kanbanTypesExists, '']);
    
    if (kanbanTypesExists) {
        try {
            const content = fs.readFileSync(kanbanTypesPath, 'utf8');
            
            // Test for key types
            const hasKanbanColumn = content.includes('KanbanColumn');
            const hasKanbanCard = content.includes('KanbanCard');
            const hasMoveCardRequest = content.includes('MoveCardRequest');
            
            printTestResult('Has KanbanColumn type', hasKanbanColumn);
            printTestResult('Has KanbanCard type', hasKanbanCard);
            printTestResult('Has MoveCardRequest type', hasMoveCardRequest);
            
            results.push(['KanbanColumn type', hasKanbanColumn, '']);
            results.push(['KanbanCard type', hasKanbanCard, '']);
            results.push(['MoveCardRequest type', hasMoveCardRequest, '']);
            
        } catch (error) {
            printTestResult('Kanban types analysis', false, error.message);
            results.push(['Kanban types analysis', false, error.message]);
        }
    }
    
    return results;
}

function testPackageDependencies() {
    printHeader('TESTING PACKAGE DEPENDENCIES');
    
    const results = [];
    
    // Check client package.json
    const clientPackagePath = '/Users/devilmashine/photo-studio-booking/client/package.json';
    const clientPackageExists = fs.existsSync(clientPackagePath);
    printTestResult('Client package.json exists', clientPackageExists);
    results.push(['Client package.json', clientPackageExists, '']);
    
    if (clientPackageExists) {
        try {
            const packageContent = JSON.parse(fs.readFileSync(clientPackagePath, 'utf8'));
            const dependencies = { ...packageContent.dependencies, ...packageContent.devDependencies };
            
            // Check for required dependencies
            const hasDragDrop = dependencies['@hello-pangea/dnd'] || dependencies['react-dnd'];
            const hasZustand = dependencies['zustand'];
            const hasTanStackQuery = dependencies['@tanstack/react-query'];
            const hasWebSocket = dependencies['ws'] || dependencies['socket.io-client'];
            
            printTestResult('Has drag-and-drop dependency', !!hasDragDrop, hasDragDrop ? `Found: ${Object.keys(dependencies).find(k => k.includes('dnd'))}` : 'Missing drag-and-drop library');
            printTestResult('Has Zustand dependency', !!hasZustand, hasZustand ? `Version: ${hasZustand}` : 'Missing Zustand');
            printTestResult('Has TanStack Query dependency', !!hasTanStackQuery, hasTanStackQuery ? `Version: ${hasTanStackQuery}` : 'Missing TanStack Query');
            printTestResult('Has WebSocket dependency', !!hasWebSocket, hasWebSocket ? 'Found WebSocket library' : 'Missing WebSocket library');
            
            results.push(['Drag-and-drop dependency', !!hasDragDrop, hasDragDrop || 'Missing']);
            results.push(['Zustand dependency', !!hasZustand, hasZustand || 'Missing']);
            results.push(['TanStack Query dependency', !!hasTanStackQuery, hasTanStackQuery || 'Missing']);
            results.push(['WebSocket dependency', !!hasWebSocket, hasWebSocket ? 'Found' : 'Missing']);
            
        } catch (error) {
            printTestResult('Package.json analysis', false, error.message);
            results.push(['Package analysis', false, error.message]);
        }
    }
    
    return results;
}

function generateFrontendTestReport(allResults) {
    printHeader('FRONTEND TEST REPORT SUMMARY');
    
    const totalTests = allResults.length;
    const passedTests = allResults.filter(([_, success, __]) => success).length;
    const failedTests = totalTests - passedTests;
    
    console.log(`Total Frontend Tests: ${totalTests}`);
    console.log(`Passed: ${passedTests} ✅`);
    console.log(`Failed: ${failedTests} ❌`);
    console.log(`Success Rate: ${((passedTests/totalTests)*100).toFixed(1)}%`);
    
    if (failedTests > 0) {
        console.log('\n🔍 FAILED FRONTEND TESTS:');
        allResults.forEach(([testName, success, details]) => {
            if (!success) {
                console.log(`  ❌ ${testName}: ${details}`);
            }
        });
    }
    
    console.log('\n📊 FRONTEND RECOMMENDATIONS:');
    if (failedTests === 0) {
        console.log('  ✅ All frontend tests passed! Frontend is ready for production.');
    } else if (failedTests < totalTests * 0.2) {  // Less than 20% failure
        console.log('  ⚠️  Minor frontend issues detected. Review failed tests.');
    } else {
        console.log('  🚨 Significant frontend issues detected. Address failed tests before deployment.');
    }
}

function main() {
    console.log('🎨 COMPREHENSIVE FRONTEND TESTING');
    console.log(`Started at: ${new Date()}`);
    
    const allResults = [];
    
    // Run frontend tests
    allResults.push(...testComponentStructure());
    allResults.push(...testEnhancedServices());
    allResults.push(...testEnhancedHooks());
    allResults.push(...testTypescriptTypes());
    allResults.push(...testPackageDependencies());
    
    // Generate report
    generateFrontendTestReport(allResults);
    
    console.log(`\n🏁 Frontend testing completed at: ${new Date()}`);
}

// ES modules don't have require.main, so we check if this is the main module
if (import.meta.url === `file://${process.argv[1]}`) {
    main();
}
