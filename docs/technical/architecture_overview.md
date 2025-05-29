# Architecture Overview

© 2025 AustralMetrics SpA. All rights reserved.

## System Architecture

The PASCAL NDVI Block follows a modular, layered architecture designed for maintainability, testability, and ISO 42001 compliance. The system is built around three core principles: simplicity, reliability, and auditability.

## High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface Layer                 │
├─────────────────────────────────────────────────────────────┤
│  CLI Interface (Typer)     │     Direct API Access          │
└─────────────────────────────────────────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────┐
│                    Orchestration Layer                     │
├─────────────────────────────────────────────────────────────┤
│  Main Controller (src.main)                                │
│  • Process coordination                                     │
│  • Error handling                                          │
│  • Result aggregation                                      │
└─────────────────────────────────────────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────┐
│                   Processing Layer                          │
├─────────────────┬─────────────────┬─────────────────────────┤
│  Preprocessor   │    Indices      │    Validation           │
│  • Clipping     │    • NDVI       │    • Input checks       │
│  • Resampling   │    • NDRE       │    • Format validation  │
│  • Validation   │    • SAVI       │    • CRS verification   │
└─────────────────┴─────────────────┴─────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                             │
├─────────────────┬─────────────────┬─────────────────────────┤
│  Input Data     │   Temporary     │    Output Data          │
│  • Satellite    │   Processing    │    • Indices (GeoTIFF)  │
│    imagery      │   • Memory      │    • Metadata (JSON)    │
│  • Vector data  │   • Disk cache  │    • Logs (Text)        │
└─────────────────┴─────────────────┴─────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────┐
│                   Infrastructure Layer                      │
├─────────────────────────────────────────────────────────────┤
│  Logging (Loguru)  │  File I/O (Rasterio)  │  Config Mgmt   │
│  • Audit trails    │  • Geospatial data    │  • Environment  │
│  • Error tracking  │  • Format support     │  • Parameters   │
└─────────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. User Interface Layer

#### CLI Interface (`typer` framework)
- **Purpose**: Provides command-line access to all functionality
- **Commands**: `indices`, `clip`, `auto`
- **Features**: 
  - Parameter validation
  - Help system
  - Progress indicators
  - Error reporting

#### Direct API Access
- **Purpose**: Programmatic access for integration
- **Interface**: Python function calls
- **Features**:
  - Type hints
  - Comprehensive documentation
  - Consistent return formats

### 2. Orchestration Layer

#### Main Controller (`src.main`)

```python
class ProcessingController:
    """
    Central coordinator for all processing operations.
    Implements command pattern for operation management.
    """
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.config = self._load_configuration()
    
    def execute_command(self, command: str, **kwargs) -> Dict[str, Any]:
        """Execute processing command with full audit trail."""
        pass
```

**Responsibilities**:
- Command routing and execution
- Error handling and recovery
- Result aggregation
- Audit logging
- Resource management

**Design Patterns**:
- **Command Pattern**: For operation encapsulation
- **Chain of Responsibility**: For error handling
- **Observer Pattern**: For progress reporting

### 3. Processing Layer

#### Preprocessor Module (`src.preprocessor`)

```python
class ImagePreprocessor:
    """
    Handles all image preprocessing operations.
    Follows single responsibility principle.
    """
    
    @staticmethod
    def validate_input(image_path: str) -> ValidationResult:
        """Validate input image format and accessibility."""
        pass
    
    @staticmethod
    def clip_image(image_path: str, vector_path: str) -> str:
        """Clip image using vector geometry."""
        pass
```

**Architecture**:
- **Static Methods**: Stateless operations for thread safety
- **Validation Pipeline**: Multi-step input verification
- **Error Propagation**: Structured error reporting

#### Indices Module (`src.indices`)

```python
class VegetationIndices:
    """
    Calculates vegetation indices with automatic band detection.
    Optimized for memory efficiency and processing speed.
    """
    
    def __init__(self, image_metadata: Dict):
        self.bands = self._detect_bands(image_metadata)
        self.nodata_value = self._get_nodata_value(image_metadata)
    
    def calculate_all_indices(self) -> Dict[str, numpy.ndarray]:
        """Calculate NDVI, NDRE, and SAVI in single pass."""
        pass
```

**Architecture**:
- **Factory Pattern**: For index calculation strategy selection
- **Template Method**: For common calculation workflow
- **Strategy Pattern**: For different satellite sensor support

### 4. Data Layer Architecture

#### Data Flow Pattern

```
Input Validation → Memory Loading → Processing → Output Writing → Cleanup
      ↓                 ↓              ↓            ↓           ↓
   Checksums     →   Chunking    →  Parallel   →  Atomic   →  Resource
   Format check     Memory mgmt     Processing     Write      Release
```

#### Storage Strategy

**Input Data Management**:
- Read-only access patterns
- Memory-mapped files for large imagery
- Lazy loading for efficiency

**Temporary Processing**:
- Memory-first approach with disk fallback
- Automatic cleanup on completion/error
- Chunk-based processing for large datasets

**Output Data Management**:
- Atomic write operations
- Metadata preservation
- Backup creation for critical results

### 5. Infrastructure Layer

#### Logging Architecture (`loguru`)

```python
class AuditLogger:
    """
    ISO 42001 compliant logging system.
    Provides full audit trail for all operations.
    """
    
    def __init__(self):
        self.logger = self._configure_loguru()
        self.session_id = self._generate_session_id()
    
    def log_operation(self, operation: str, inputs: Dict, 
                     outputs: Dict, duration: float):
        """Log operation with full context."""
        pass
```

**Features**:
- **Structured Logging**: JSON-formatted entries
- **Automatic Rotation**: Size and time-based rotation
- **Integrity Protection**: SHA-256 checksums
- **Backup Management**: Automated backup creation

#### Configuration Management

```python
class ConfigurationManager:
    """
    Centralized configuration management.
    Environment-aware with validation.
    """
    
    def __init__(self):
        self.config = self._load_from_env()
        self._validate_configuration()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with fallback."""
        pass
```

## Design Principles

### 1. Single Responsibility Principle
Each module has a clear, single purpose:
- `main.py`: Orchestration only
- `indices.py`: Index calculations only
- `preprocessor.py`: Image preprocessing only

### 2. Dependency Inversion
High-level modules don't depend on low-level modules:
- Abstract interfaces for external dependencies
- Dependency injection for testing
- Configuration-driven behavior

### 3. Open/Closed Principle
System is open for extension, closed for modification:
- Plugin architecture for new indices
- Strategy pattern for different sensors
- Configuration-based feature flags

### 4. Interface Segregation
Clients depend only on interfaces they use:
- Minimal public APIs
- Role-based interfaces
- Clear separation of concerns

## Quality Assurance Architecture

### Testing Strategy

**Unit Testing**:
```python
class TestIndicesModule:
    """Comprehensive unit tests for indices calculation."""
    
    def test_ndvi_calculation_accuracy(self):
        """Test NDVI calculation against known values."""
        pass
    
    def test_band_detection_sentinel2(self):
        """Test automatic band detection for Sentinel-2."""
        pass
```

**Integration Testing**:
- End-to-end workflow testing
- Error condition simulation
- Performance benchmarking

**Continuous Integration**:
- Automated testing on every commit
- Code quality checks (flake8, mypy)
- Documentation generation
- Security vulnerability scanning

### Performance Architecture

**Memory Management**:
- Streaming processing for large files
- Garbage collection optimization
- Memory usage monitoring

**Processing Optimization**:
- NumPy vectorization
- Parallel processing where applicable
- Efficient I/O operations
- Caching strategies

## Security Architecture

### Data Protection
- Input validation and sanitization
- Path traversal prevention
- Temporary file secure handling
- Output data integrity verification

### Audit and Compliance
- Complete operation logging
- User action tracking
- System state monitoring
- Compliance report generation

## Deployment Architecture

### Environment Management
```
Development → Testing → Staging → Production
     ↓          ↓         ↓          ↓
   Local     CI/CD    Pre-prod   Live System
  Testing   Pipeline   Testing   Monitoring
```

### Packaging Strategy
- Virtual environment isolation
- Dependency pinning
- Cross-platform compatibility
- Distribution package creation

## Scalability Considerations

### Current Architecture Limits
- **Single Machine**: Designed for standalone operation
- **Memory Bound**: Limited by available system memory
- **I/O Bound**: Limited by disk read/write speed

### Future Scalability Options
- **Distributed Processing**: Chunked processing across nodes
- **Cloud Integration**: S3/Azure Blob storage support
- **Container Deployment**: Docker containerization
- **API Service**: REST API for remote access

## Monitoring and Observability

### System Metrics
- Processing time per operation
- Memory usage patterns
- Error rates and types
- File I/O performance

### Business Metrics
- Images processed per day
- Success/failure rates
- User activity patterns
- Feature usage statistics

## Maintenance Architecture

### Code Maintenance
- Automated dependency updates
- Regular security patches
- Performance monitoring
- Refactoring guidelines

### Data Maintenance
- Log rotation and archival
- Temporary file cleanup
- Result data retention
- Backup verification

## Integration Points

### External System Integration
- **GIS Software**: QGIS, ArcGIS compatibility
- **Data Pipelines**: Integration with larger workflows
- **Cloud Platforms**: AWS, Azure, GCP support
- **Databases**: Metadata storage options

### API Integration
- RESTful interface considerations
- Authentication mechanisms
- Rate limiting strategies
- Version management

## Risk Management

### Technical Risks
- **Data Corruption**: Checksums and validation
- **Processing Failures**: Robust error handling
- **Resource Exhaustion**: Memory and disk monitoring
- **Version Conflicts**: Dependency management

### Mitigation Strategies
- Comprehensive testing
- Graceful degradation
- Automatic recovery
- Clear error reporting

This architecture supports the ISO 42001 requirements while maintaining simplicity and reliability for end users.